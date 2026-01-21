"""Legal Service - Legal awareness and guidance"""

from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from loguru import logger
from edge_server.models.database import LegalTopic, LegalQuery
import hashlib
from datetime import datetime

async def handle_legal_intent(user_id: str, transcript: str, language: str, db: AsyncSession, model_manager) -> str:
    """Handle legal awareness intents"""
    try:
        # Hash the query for privacy
        query_hash = hashlib.sha256(transcript.encode()).hexdigest()[:16]
        
        # Detect legal topic
        topic = detect_legal_topic(transcript)
        
        # Get relevant legal information
        legal_info = await get_legal_information(topic, language, db)
        
        if legal_info:
            response_text = legal_info.content
        else:
            # Use AI to generate response
            response_text = await generate_legal_response(transcript, language, model_manager)
        
        # Log query (anonymized)
        log_query = LegalQuery(
            user_id=user_id,
            query_hash=query_hash,
            topic_category=topic,
            language=language,
            response_summary=response_text[:200],
            created_at=datetime.utcnow()
        )
        db.add(log_query)
        await db.commit()
        
        return response_text
        
    except Exception as e:
        logger.error(f"Legal intent error: {e}")
        return get_legal_error_message(language)

def detect_legal_topic(transcript: str) -> str:
    """Detect legal topic from transcript"""
    transcript_lower = transcript.lower()
    
    keywords = {
        "labor_rights": ["मजदूरी", "wage", "labor", "काम", "नौकरी"],
        "safety_laws": ["सुरक्षा", "safety", "हिंसा", "violence"],
        "domestic_violence": ["घरेलू", "domestic", "मारपीट"],
        "property_rights": ["संपत्ति", "property", "जमीन", "land"],
        "financial_rights": ["पैसा", "money", "बैंक", "bank", "loan"],
        "workplace_harassment": ["उत्पीड़न", "harassment", "workplace"]
    }
    
    for topic, words in keywords.items():
        if any(word in transcript_lower for word in words):
            return topic
    
    return "general"

async def get_legal_information(topic: str, language: str, db: AsyncSession) -> LegalTopic:
    """Get legal information from database"""
    result = await db.execute(
        select(LegalTopic).where(
            LegalTopic.category == topic,
            LegalTopic.language == language,
            LegalTopic.is_active == True
        )
    )
    return result.scalar_one_or_none()

async def generate_legal_response(transcript: str, language: str, model_manager) -> str:
    """Generate legal response using AI"""
    context = {
        "user_query": transcript,
        "language": language,
        "disclaimer": "This is general information, not legal advice"
    }
    
    response = await model_manager.generate_response(
        {"intent": "legal"},
        context
    )
    
    # Add disclaimer
    disclaimer = {
        "hi": "यह सामान्य जानकारी है, कानूनी सलाह नहीं। विशेष मामलों के लिए कानूनी विशेषज्ञ से परामर्श लें।"
    }
    
    return response + " " + disclaimer.get(language, "")

def get_legal_error_message(language: str) -> str:
    """Get error message for legal queries"""
    return {
        "hi": "कानूनी जानकारी प्राप्त करने में समस्या हुई। कृपया बाद में प्रयास करें।"
    }.get(language, "Error accessing legal information")

async def list_legal_topics(language: str, db: AsyncSession) -> Dict[str, Any]:
    """List available legal topics"""
    result = await db.execute(
        select(LegalTopic).where(
            LegalTopic.language == language,
            LegalTopic.is_active == True
        )
    )
    topics = result.scalars().all()
    
    return {
        "topics": [
            {
                "id": t.id,
                "name": t.name,
                "description": t.description,
                "category": t.category
            }
            for t in topics
        ]
    }
