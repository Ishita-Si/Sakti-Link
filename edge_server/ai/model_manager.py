"""
AI Model Manager for Sakti-Link Edge Server
Manages loading and inference for all AI models
"""

import os
import asyncio
from typing import Optional, Dict, Any, List
from loguru import logger
from pathlib import Path
import hashlib

from edge_server.core.config import settings


class ModelManager:
    """Manages all AI models for the edge server"""
    
    def __init__(self):
        self.models = {}
        self.model_loaded = {
            "whisper": False,
            "llama": False,
            "sentence_transformer": False,
            "tts": False
        }
        
    async def initialize(self):
        """Initialize all AI models"""
        logger.info("Initializing AI models...")
        
        try:
            # Load models in parallel for faster startup
            await asyncio.gather(
                self._load_whisper_model(),
                self._load_llama_model(),
                self._load_sentence_transformer(),
                self._setup_tts(),
                return_exceptions=True
            )
            
            logger.info("AI models initialization complete")
            logger.info(f"Loaded models: {[k for k, v in self.model_loaded.items() if v]}")
            
        except Exception as e:
            logger.error(f"Failed to initialize models: {e}")
            raise
    
    async def _load_whisper_model(self):
        """Load Whisper model for speech recognition"""
        try:
            logger.info("Loading Whisper model...")
            
            # In production, load actual Whisper model
            # For now, using a placeholder
            from transformers import WhisperProcessor, WhisperForConditionalGeneration
            
            model_path = Path(settings.MODELS_DIR) / "whisper"
            
            if model_path.exists():
                processor = WhisperProcessor.from_pretrained(str(model_path))
                model = WhisperForConditionalGeneration.from_pretrained(str(model_path))
            else:
                # Download and cache
                logger.warning(f"Whisper model not found locally, will use API fallback")
                processor = None
                model = None
            
            self.models["whisper_processor"] = processor
            self.models["whisper_model"] = model
            self.model_loaded["whisper"] = True
            
            logger.info("Whisper model loaded successfully")
            
        except Exception as e:
            logger.warning(f"Failed to load Whisper model: {e}. Will use Bhashini API.")
            self.model_loaded["whisper"] = False
    
    async def _load_llama_model(self):
        """Load Llama model for intent understanding and reasoning"""
        try:
            logger.info("Loading Llama model...")
            
            # Use llama-cpp-python for quantized models
            from llama_cpp import Llama
            
            model_path = Path(settings.MODELS_DIR) / settings.LLAMA_MODEL_FILE
            
            if model_path.exists():
                llm = Llama(
                    model_path=str(model_path),
                    n_ctx=2048,  # Context window
                    n_threads=4,  # CPU threads
                    n_gpu_layers=0,  # CPU only for edge devices
                    verbose=False
                )
                self.models["llama"] = llm
                self.model_loaded["llama"] = True
                logger.info("Llama model loaded successfully")
            else:
                logger.warning(f"Llama model not found at {model_path}")
                self.model_loaded["llama"] = False
                
        except Exception as e:
            logger.warning(f"Failed to load Llama model: {e}")
            self.model_loaded["llama"] = False
    
    async def _load_sentence_transformer(self):
        """Load sentence transformer for semantic search"""
        try:
            logger.info("Loading Sentence Transformer...")
            
            from sentence_transformers import SentenceTransformer
            
            model_path = Path(settings.MODELS_DIR) / "sentence_transformer"
            
            if model_path.exists():
                model = SentenceTransformer(str(model_path))
            else:
                # Use lightweight multilingual model
                model = SentenceTransformer(settings.SENTENCE_TRANSFORMER_MODEL)
                model.save(str(model_path))
            
            self.models["sentence_transformer"] = model
            self.model_loaded["sentence_transformer"] = True
            
            logger.info("Sentence Transformer loaded successfully")
            
        except Exception as e:
            logger.warning(f"Failed to load Sentence Transformer: {e}")
            self.model_loaded["sentence_transformer"] = False
    
    async def _setup_tts(self):
        """Setup TTS engine"""
        try:
            logger.info("Setting up TTS engine...")
            
            # For production, integrate with Bhashini or other TTS
            # For now, placeholder
            self.models["tts"] = {"engine": "bhashini", "ready": True}
            self.model_loaded["tts"] = True
            
            logger.info("TTS engine ready")
            
        except Exception as e:
            logger.warning(f"Failed to setup TTS: {e}")
            self.model_loaded["tts"] = False
    
    async def speech_to_text(self, audio_data: bytes, language: str = "hi") -> Dict[str, Any]:
        """
        Convert speech to text
        
        Args:
            audio_data: Audio data in bytes
            language: Language code
        
        Returns:
            Dict with transcript and confidence
        """
        try:
            # If Whisper model is loaded, use it
            if self.model_loaded["whisper"] and self.models.get("whisper_model"):
                # Implement Whisper inference
                # For now, placeholder
                transcript = await self._whisper_inference(audio_data, language)
            else:
                # Use Bhashini API
                transcript = await self._bhashini_stt(audio_data, language)
            
            return {
                "success": True,
                "transcript": transcript,
                "language": language,
                "confidence": 0.95  # Placeholder
            }
            
        except Exception as e:
            logger.error(f"Speech-to-text error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _whisper_inference(self, audio_data: bytes, language: str) -> str:
        """Perform Whisper inference"""
        # Placeholder implementation
        return "Transcribed text from Whisper"
    
    async def _bhashini_stt(self, audio_data: bytes, language: str) -> str:
        """Call Bhashini API for STT"""
        # Placeholder - integrate with actual Bhashini API
        logger.info(f"Using Bhashini STT for language: {language}")
        return "Transcribed text from Bhashini"
    
    async def text_to_speech(self, text: str, language: str = "hi") -> bytes:
        """
        Convert text to speech
        
        Args:
            text: Text to convert
            language: Language code
        
        Returns:
            Audio data in bytes
        """
        try:
            # Use Bhashini TTS
            audio_data = await self._bhashini_tts(text, language)
            return audio_data
            
        except Exception as e:
            logger.error(f"Text-to-speech error: {e}")
            raise
    
    async def _bhashini_tts(self, text: str, language: str) -> bytes:
        """Call Bhashini API for TTS"""
        # Placeholder - integrate with actual Bhashini API
        logger.info(f"Using Bhashini TTS for language: {language}")
        return b"audio_data_placeholder"
    
    async def understand_intent(self, transcript: str, language: str = "hi") -> Dict[str, Any]:
        """
        Understand user intent from transcript
        
        Args:
            transcript: User's spoken text
            language: Language code
        
        Returns:
            Dict with intent, entities, and confidence
        """
        try:
            if self.model_loaded["llama"]:
                intent = await self._llama_intent(transcript, language)
            else:
                # Simple rule-based fallback
                intent = self._rule_based_intent(transcript)
            
            return intent
            
        except Exception as e:
            logger.error(f"Intent understanding error: {e}")
            return {
                "intent": "unknown",
                "entities": {},
                "confidence": 0.0
            }
    
    async def _llama_intent(self, transcript: str, language: str) -> Dict[str, Any]:
        """Use Llama for intent classification"""
        llm = self.models["llama"]
        
        prompt = f"""You are a helpful assistant for Sakti-Link, a platform for women's empowerment.
Classify the user's intent into one of these categories:
- learn: User wants to learn something
- earn: User wants to find work/gigs
- legal: User has legal questions
- skill_swap: User wants to teach or learn skills
- help: User needs general help
- greeting: User is greeting or making small talk

User message: {transcript}

Respond with ONLY a JSON object: {{"intent": "...", "confidence": 0.0-1.0, "entities": {{}}}}
"""
        
        response = llm(prompt, max_tokens=100, temperature=0.1, stop=["}", "\n\n"])
        
        # Parse response
        try:
            import json
            result = json.loads(response["choices"][0]["text"] + "}")
            return result
        except:
            return self._rule_based_intent(transcript)
    
    def _rule_based_intent(self, transcript: str) -> Dict[str, Any]:
        """Simple rule-based intent classification"""
        transcript_lower = transcript.lower()
        
        # Learning keywords (Hindi and English)
        learn_keywords = ["सीखना", "learn", "पढ़ना", "study", "कोर्स", "course"]
        earn_keywords = ["काम", "work", "नौकरी", "job", "earn", "पैसा", "money"]
        legal_keywords = ["कानून", "law", "legal", "अधिकार", "rights", "न्याय", "justice"]
        skill_keywords = ["skill", "सिखाना", "teach", "हुनर", "talent"]
        
        if any(keyword in transcript_lower for keyword in learn_keywords):
            return {"intent": "learn", "confidence": 0.8, "entities": {}}
        elif any(keyword in transcript_lower for keyword in earn_keywords):
            return {"intent": "earn", "confidence": 0.8, "entities": {}}
        elif any(keyword in transcript_lower for keyword in legal_keywords):
            return {"intent": "legal", "confidence": 0.8, "entities": {}}
        elif any(keyword in transcript_lower for keyword in skill_keywords):
            return {"intent": "skill_swap", "confidence": 0.8, "entities": {}}
        else:
            return {"intent": "unknown", "confidence": 0.5, "entities": {}}
    
    async def generate_response(self, intent: Dict[str, Any], context: Dict[str, Any]) -> str:
        """
        Generate natural language response
        
        Args:
            intent: Detected intent
            context: Conversation context
        
        Returns:
            Response text
        """
        try:
            if self.model_loaded["llama"]:
                response = await self._llama_generate(intent, context)
            else:
                # Template-based fallback
                response = self._template_response(intent, context)
            
            return response
            
        except Exception as e:
            logger.error(f"Response generation error: {e}")
            return "मैं आपकी मदद करने के लिए यहाँ हूँ। कृपया फिर से प्रयास करें।"
    
    async def _llama_generate(self, intent: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Use Llama for response generation"""
        llm = self.models["llama"]
        
        prompt = f"""You are a friendly AI assistant for Sakti-Link, helping women with learning, earning, and legal awareness.

Intent: {intent['intent']}
Context: {context}

Generate a helpful, concise response in Hindi. Be warm and encouraging.

Response:"""
        
        response = llm(prompt, max_tokens=200, temperature=0.7)
        return response["choices"][0]["text"].strip()
    
    def _template_response(self, intent: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Template-based response"""
        intent_type = intent.get("intent", "unknown")
        
        templates = {
            "learn": "मैं आपको सीखने में मदद कर सकती हूँ। क्या आप किसी विशेष विषय में रुचि रखती हैं?",
            "earn": "मैं आपके लिए काम खोजने में मदद कर सकती हूँ। आप किस प्रकार का काम ढूंढ रही हैं?",
            "legal": "मैं आपके कानूनी सवालों में मदद कर सकती हूँ। कृपया अपना सवाल पूछें।",
            "skill_swap": "आप अपने कौशल साझा कर सकती हैं या नए कौशल सीख सकती हैं। आप क्या करना चाहेंगी?",
            "greeting": "नमस्ते! मैं सक्ति-लिंक हूँ। मैं आपकी कैसे मदद कर सकती हूँ?",
            "unknown": "मुझे खेद है, मैं समझ नहीं पाई। क्या आप फिर से कह सकती हैं?"
        }
        
        return templates.get(intent_type, templates["unknown"])
    
    async def semantic_search(self, query: str, documents: List[str], top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Perform semantic search on documents
        
        Args:
            query: Search query
            documents: List of documents to search
            top_k: Number of top results to return
        
        Returns:
            List of results with scores
        """
        try:
            if not self.model_loaded["sentence_transformer"]:
                logger.warning("Sentence transformer not loaded, using simple search")
                return self._simple_search(query, documents, top_k)
            
            model = self.models["sentence_transformer"]
            
            # Encode query and documents
            query_embedding = model.encode(query)
            doc_embeddings = model.encode(documents)
            
            # Calculate similarities
            from sklearn.metrics.pairwise import cosine_similarity
            similarities = cosine_similarity([query_embedding], doc_embeddings)[0]
            
            # Get top results
            top_indices = similarities.argsort()[-top_k:][::-1]
            
            results = [
                {
                    "document": documents[i],
                    "score": float(similarities[i]),
                    "index": int(i)
                }
                for i in top_indices
            ]
            
            return results
            
        except Exception as e:
            logger.error(f"Semantic search error: {e}")
            return []
    
    def _simple_search(self, query: str, documents: List[str], top_k: int) -> List[Dict[str, Any]]:
        """Simple keyword-based search fallback"""
        query_lower = query.lower()
        results = []
        
        for i, doc in enumerate(documents):
            # Simple word overlap score
            doc_lower = doc.lower()
            query_words = set(query_lower.split())
            doc_words = set(doc_lower.split())
            overlap = len(query_words.intersection(doc_words))
            
            if overlap > 0:
                results.append({
                    "document": doc,
                    "score": overlap / len(query_words),
                    "index": i
                })
        
        # Sort by score
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]
    
    async def cleanup(self):
        """Cleanup models and free resources"""
        logger.info("Cleaning up AI models...")
        self.models.clear()
        self.model_loaded = {k: False for k in self.model_loaded}
        logger.info("AI models cleanup complete")
