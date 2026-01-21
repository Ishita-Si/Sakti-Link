"""Gig Service - Micro-gig marketplace logic"""

from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from loguru import logger
from datetime import datetime, timedelta
from edge_server.models.database import Gig, GigApplication, User
import math

async def handle_gig_intent(user_id: str, transcript: str, language: str, db: AsyncSession) -> str:
    """Handle gig-related intents"""
    try:
        transcript_lower = transcript.lower()
        
        if any(word in transcript_lower for word in ["find", "खोजना", "ढूंढना", "काम"]):
            # User wants to find gigs
            gigs = await get_available_gigs(user_id, language, db)
            if gigs:
                return format_gig_list(gigs, language)
            return {"hi": "अभी कोई काम उपलब्ध नहीं है। कृपया बाद में देखें।"}.get(language, "No gigs available")
        
        elif any(word in transcript_lower for word in ["my", "mera", "मेरा", "status"]):
            # User wants to check their applications
            apps = await get_user_applications(user_id, db)
            return format_application_status(apps, language)
        
        else:
            return {"hi": "मैं आपके लिए काम ढूंढ सकती हूँ। आप किस प्रकार का काम चाहती हैं?"}.get(language, "I can help you find work")
            
    except Exception as e:
        logger.error(f"Gig intent error: {e}")
        return {"hi": "काम खोजने में समस्या हुई।"}.get(language, "Error finding gigs")

async def get_available_gigs(user_id: str, language: str, db: AsyncSession, limit: int = 5) -> List[Gig]:
    """Get available gigs for user"""
    result = await db.execute(
        select(Gig)
        .where(and_(
            Gig.status == "open",
            Gig.expires_at > datetime.utcnow()
        ))
        .order_by(Gig.created_at.desc())
        .limit(limit)
    )
    return result.scalars().all()

async def apply_for_gig(user_id: str, gig_id: int, db: AsyncSession) -> Dict[str, Any]:
    """Apply for a gig"""
    # Check if already applied
    existing = await db.execute(
        select(GigApplication).where(and_(
            GigApplication.user_id == user_id,
            GigApplication.gig_id == gig_id
        ))
    )
    if existing.scalar_one_or_none():
        return {"success": False, "error": "Already applied"}
    
    application = GigApplication(user_id=user_id, gig_id=gig_id, status="pending")
    db.add(application)
    await db.commit()
    return {"success": True, "application_id": application.id}

async def get_user_applications(user_id: str, db: AsyncSession) -> List[GigApplication]:
    """Get user's gig applications"""
    result = await db.execute(
        select(GigApplication)
        .where(GigApplication.user_id == user_id)
        .order_by(GigApplication.applied_at.desc())
        .limit(10)
    )
    return result.scalars().all()

def format_gig_list(gigs: List[Gig], language: str) -> str:
    """Format gig list for voice response"""
    intro = {"hi": "ये काम उपलब्ध हैं: "}.get(language, "Available gigs: ")
    gig_items = [f"{g.title} - {g.payment} रुपये" for g in gigs[:3]]
    return intro + ", ".join(gig_items) + ". कौनसे काम में रुचि है?"

def format_application_status(apps: List[GigApplication], language: str) -> str:
    """Format application status"""
    if not apps:
        return {"hi": "आपने अभी तक किसी काम के लिए आवेदन नहीं किया है।"}.get(language, "No applications yet")
    pending = sum(1 for a in apps if a.status == "pending")
    accepted = sum(1 for a in apps if a.status == "accepted")
    return {"hi": f"आपके {pending} आवेदन लंबित हैं और {accepted} स्वीकार किए गए हैं।"}.get(language, f"{pending} pending, {accepted} accepted")
