"""
Voice API endpoints for Sakti-Link Edge Server
Handles voice input/output and intent routing
"""

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Request
from fastapi.responses import Response
from pydantic import BaseModel
from typing import Optional, Dict, Any
from loguru import logger
from edge_server.db.database import get_db_session
from sqlalchemy.ext.asyncio import AsyncSession
from edge_server.models.database import User, SystemMetrics
from datetime import datetime
import hashlib
import base64

router = APIRouter()


class VoiceProcessRequest(BaseModel):
    """Request for processing voice input"""
    audio_base64: Optional[str] = None  # Base64 encoded audio
    language: str = "hi"
    device_fingerprint: str


class VoiceProcessResponse(BaseModel):
    """Response from voice processing"""
    success: bool
    transcript: Optional[str] = None
    intent: Optional[Dict[str, Any]] = None
    response_text: str
    response_audio_base64: Optional[str] = None
    next_action: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class TTSRequest(BaseModel):
    """Request for text-to-speech"""
    text: str
    language: str = "hi"


@router.post("/process", response_model=VoiceProcessResponse)
async def process_voice_input(
    request: Request,
    voice_request: VoiceProcessRequest,
    db: AsyncSession = Depends(get_db_session)
):
    """
    Process voice input and return voice response
    
    Main entry point for voice interactions
    Flow: Audio -> STT -> Intent Understanding -> Response Generation -> TTS -> Audio
    """
    try:
        logger.info(f"Processing voice input in language: {voice_request.language}")
        
        # Get or create user
        user = await get_or_create_user(db, voice_request.device_fingerprint, voice_request.language)
        
        # Decode audio
        if not voice_request.audio_base64:
            raise HTTPException(status_code=400, detail="No audio data provided")
        
        audio_data = base64.b64decode(voice_request.audio_base64)
        
        # Get model manager from app state
        model_manager = request.app.state.model_manager
        
        # Step 1: Speech to Text
        stt_result = await model_manager.speech_to_text(audio_data, voice_request.language)
        
        if not stt_result.get("success"):
            raise HTTPException(status_code=500, detail="Speech recognition failed")
        
        transcript = stt_result["transcript"]
        logger.info(f"Transcript: {transcript}")
        
        # Step 2: Understand Intent
        intent = await model_manager.understand_intent(transcript, voice_request.language)
        logger.info(f"Detected intent: {intent}")
        
        # Step 3: Route to appropriate handler
        response_text = await route_intent(
            intent=intent,
            transcript=transcript,
            user_id=user.id,
            language=voice_request.language,
            db=db,
            request=request
        )
        
        # Step 4: Text to Speech
        response_audio = await model_manager.text_to_speech(response_text, voice_request.language)
        response_audio_base64 = base64.b64encode(response_audio).decode('utf-8')
        
        # Log metrics
        await log_metric(
            db=db,
            metric_type="voice_interaction",
            language=voice_request.language,
            metadata={"intent": intent["intent"]}
        )
        
        # Update user last active
        user.last_active = datetime.utcnow()
        await db.commit()
        
        return VoiceProcessResponse(
            success=True,
            transcript=transcript,
            intent=intent,
            response_text=response_text,
            response_audio_base64=response_audio_base64,
            next_action=intent.get("intent"),
            metadata={
                "confidence": intent.get("confidence", 0.0),
                "processing_time": "0.5s"  # Placeholder
            }
        )
        
    except Exception as e:
        logger.error(f"Voice processing error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/synthesize")
async def synthesize_speech(
    request: Request,
    tts_request: TTSRequest
):
    """
    Convert text to speech
    """
    try:
        model_manager = request.app.state.model_manager
        
        audio_data = await model_manager.text_to_speech(
            tts_request.text,
            tts_request.language
        )
        
        # Return audio as WAV
        return Response(
            content=audio_data,
            media_type="audio/wav",
            headers={
                "Content-Disposition": "attachment; filename=speech.wav"
            }
        )
        
    except Exception as e:
        logger.error(f"TTS error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def route_intent(
    intent: Dict[str, Any],
    transcript: str,
    user_id: str,
    language: str,
    db: AsyncSession,
    request: Request
) -> str:
    """
    Route intent to appropriate service and generate response
    """
    intent_type = intent.get("intent", "unknown")
    model_manager = request.app.state.model_manager
    
    try:
        if intent_type == "learn":
            # Import here to avoid circular dependency
            from edge_server.services.learning_service import handle_learning_intent
            response = await handle_learning_intent(user_id, transcript, language, db)
            
        elif intent_type == "earn":
            from edge_server.services.gig_service import handle_gig_intent
            response = await handle_gig_intent(user_id, transcript, language, db)
            
        elif intent_type == "legal":
            from edge_server.services.legal_service import handle_legal_intent
            response = await handle_legal_intent(user_id, transcript, language, db, model_manager)
            
        elif intent_type == "skill_swap":
            from edge_server.services.skill_service import handle_skill_intent
            response = await handle_skill_intent(user_id, transcript, language, db)
            
        elif intent_type == "greeting":
            response = get_greeting_response(language)
            
        else:
            response = get_unknown_intent_response(language)
        
        return response
        
    except Exception as e:
        logger.error(f"Intent routing error: {e}")
        return get_error_response(language)


async def get_or_create_user(
    db: AsyncSession,
    device_fingerprint: str,
    language: str
) -> User:
    """Get existing user or create new one"""
    from sqlalchemy import select
    
    # Hash the device fingerprint for privacy
    fingerprint_hash = hashlib.sha256(device_fingerprint.encode()).hexdigest()
    
    # Try to find existing user
    result = await db.execute(
        select(User).where(User.device_fingerprint == fingerprint_hash)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        # Create new user
        user = User(
            device_fingerprint=fingerprint_hash,
            language_preference=language
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        
        logger.info(f"Created new user: {user.id}")
        
        # Give initial credits
        from edge_server.models.database import CreditTransaction
        from edge_server.core.config import settings
        
        credit = CreditTransaction(
            user_id=user.id,
            amount=settings.LEARNING_CREDIT_INITIAL,
            transaction_type="initial",
            description="Welcome credits"
        )
        db.add(credit)
        await db.commit()
    
    return user


async def log_metric(
    db: AsyncSession,
    metric_type: str,
    language: str,
    metadata: Dict[str, Any] = None
):
    """Log system metrics"""
    metric = SystemMetrics(
        metric_type=metric_type,
        metric_value=1.0,
        language=language,
        metadata=metadata or {}
    )
    db.add(metric)
    await db.commit()


def get_greeting_response(language: str) -> str:
    """Get greeting response in specified language"""
    greetings = {
        "hi": "नमस्ते! मैं सक्ति-लिंक हूँ। मैं आपकी सीखने, कमाने और कानूनी जागरूकता में मदद कर सकती हूँ। आप क्या करना चाहेंगी?",
        "bn": "নমস্কার! আমি সক্তি-লিঙ্ক। আমি আপনাকে শেখা, উপার্জন এবং আইনি সচেতনতায় সাহায্য করতে পারি।",
        "ta": "வணக்கம்! நான் சக்தி-லிங்க். நான் உங்களுக்கு கற்றல், சம்பாதித்தல் மற்றும் சட்ட விழிப்புணர்வில் உதவ முடியும்.",
        "te": "నమస్కారం! నేను శక్తి-లింక్. నేను మీకు నేర్చుకోవడం, సంపాదించడం మరియు చట్టపరమైన అవగాహనలో సహాయం చేయగలను.",
    }
    return greetings.get(language, greetings["hi"])


def get_unknown_intent_response(language: str) -> str:
    """Get response for unknown intent"""
    responses = {
        "hi": "मुझे खेद है, मैं आपकी बात पूरी तरह समझ नहीं पाई। आप मुझसे सीखने, काम ढूंढने, या कानूनी सवालों के बारे में पूछ सकती हैं।",
        "bn": "দুঃখিত, আমি সম্পূর্ণভাবে বুঝতে পারিনি। আপনি আমাকে শেখা, কাজ খোঁজা বা আইনি প্রশ্ন সম্পর্কে জিজ্ঞাসা করতে পারেন।",
    }
    return responses.get(language, responses["hi"])


def get_error_response(language: str) -> str:
    """Get error response"""
    responses = {
        "hi": "मुझे खेद है, कुछ गड़बड़ हो गई। कृपया फिर से प्रयास करें।",
        "bn": "দুঃখিত, কিছু ভুল হয়েছে। অনুগ্রহ করে আবার চেষ্টা করুন।",
    }
    return responses.get(language, responses["hi"])


@router.get("/languages")
async def get_supported_languages():
    """Get list of supported languages"""
    from edge_server.core.config import settings
    
    language_names = {
        "hi": "हिंदी (Hindi)",
        "bn": "বাংলা (Bengali)",
        "ta": "தமிழ் (Tamil)",
        "te": "తెలుగు (Telugu)",
        "mr": "मराठी (Marathi)",
        "gu": "ગુજરાતી (Gujarati)",
        "kn": "ಕನ್ನಡ (Kannada)",
        "ml": "മലയാളം (Malayalam)",
        "pa": "ਪੰਜਾਬੀ (Punjabi)",
        "or": "ଓଡ଼ିଆ (Odia)"
    }
    
    return {
        "languages": [
            {
                "code": lang,
                "name": language_names.get(lang, lang)
            }
            for lang in settings.SUPPORTED_LANGUAGES
        ]
    }
