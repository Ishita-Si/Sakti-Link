"""Skill Service - Skill-swap time bank"""

from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from loguru import logger
from edge_server.models.database import Skill, UserSkill, CreditTransaction
from edge_server.core.config import settings
from datetime import datetime

async def handle_skill_intent(user_id: str, transcript: str, language: str, db: AsyncSession) -> str:
    """Handle skill swap intents"""
    try:
        transcript_lower = transcript.lower()
        
        if any(word in transcript_lower for word in ["teach", "सिखाना", "सिखा"]):
            # User wants to teach
            return await handle_teach_skill(user_id, transcript, language, db)
        
        elif any(word in transcript_lower for word in ["learn", "सीखना", "सीख"]):
            # User wants to learn
            return await handle_learn_skill(user_id, transcript, language, db)
        
        else:
            return get_skill_swap_intro(language)
            
    except Exception as e:
        logger.error(f"Skill intent error: {e}")
        return get_skill_error_message(language)

async def handle_teach_skill(user_id: str, transcript: str, language: str, db: AsyncSession) -> str:
    """Handle teaching a skill"""
    messages = {
        "hi": "बहुत अच्छे! आप कौनसा कौशल सिखाना चाहती हैं? उदाहरण: सिलाई, खाना बनाना, कढ़ाई, आदि।"
    }
    return messages.get(language, "What skill do you want to teach?")

async def handle_learn_skill(user_id: str, transcript: str, language: str, db: AsyncSession) -> str:
    """Handle learning a skill"""
    # Get available skills
    result = await db.execute(
        select(UserSkill)
        .where(and_(
            UserSkill.skill_type == "teach",
            UserSkill.status == "active"
        ))
        .limit(5)
    )
    teaching_skills = result.scalars().all()
    
    if not teaching_skills:
        return {"hi": "अभी कोई कौशल सिखाने के लिए उपलब्ध नहीं है।"}.get(language, "No skills available")
    
    # Get skill details
    skill_ids = list(set(ts.skill_id for ts in teaching_skills))
    skills_result = await db.execute(
        select(Skill).where(Skill.id.in_(skill_ids))
    )
    skills = {s.id: s for s in skills_result.scalars().all()}
    
    # Format response
    skill_names = [skills[ts.skill_id].name for ts in teaching_skills[:3] if ts.skill_id in skills]
    response = {"hi": f"ये कौशल सीखने के लिए उपलब्ध हैं: {', '.join(skill_names)}। कौनसा सीखना चाहेंगी?"}.get(language, "")
    
    return response

async def register_skill_to_teach(user_id: str, skill_name: str, proficiency: int, db: AsyncSession) -> Dict[str, Any]:
    """Register a skill user wants to teach"""
    # Find or create skill
    result = await db.execute(
        select(Skill).where(Skill.name == skill_name)
    )
    skill = result.scalar_one_or_none()
    
    if not skill:
        skill = Skill(name=skill_name, category="user_contributed")
        db.add(skill)
        await db.flush()
    
    # Create user skill
    user_skill = UserSkill(
        user_id=user_id,
        skill_id=skill.id,
        skill_type="teach",
        proficiency_level=proficiency,
        status="active"
    )
    db.add(user_skill)
    await db.commit()
    
    return {"success": True, "skill_id": skill.id, "user_skill_id": user_skill.id}

async def register_skill_to_learn(user_id: str, skill_id: int, db: AsyncSession) -> Dict[str, Any]:
    """Register interest in learning a skill"""
    user_skill = UserSkill(
        user_id=user_id,
        skill_id=skill_id,
        skill_type="learn",
        status="active"
    )
    db.add(user_skill)
    await db.commit()
    
    return {"success": True, "user_skill_id": user_skill.id}

async def complete_skill_teaching_session(teacher_id: str, learner_id: str, skill_id: int, db: AsyncSession) -> Dict[str, Any]:
    """Award credits for completed teaching session"""
    # Award credits to teacher
    credit = CreditTransaction(
        user_id=teacher_id,
        amount=settings.LEARNING_CREDIT_PER_TEACH,
        transaction_type="teach",
        description=f"Taught skill: {skill_id}",
        related_skill_id=skill_id
    )
    db.add(credit)
    
    # Deduct credits from learner
    debit = CreditTransaction(
        user_id=learner_id,
        amount=settings.LEARNING_CREDIT_PER_LEARN,
        transaction_type="learn",
        description=f"Learned skill: {skill_id}",
        related_skill_id=skill_id
    )
    db.add(debit)
    
    await db.commit()
    
    return {
        "success": True,
        "teacher_credits": settings.LEARNING_CREDIT_PER_TEACH,
        "learner_credits": settings.LEARNING_CREDIT_PER_LEARN
    }

async def get_skill_marketplace(language: str, db: AsyncSession) -> Dict[str, Any]:
    """Get all available skills in marketplace"""
    # Get all teaching skills
    result = await db.execute(
        select(UserSkill, Skill)
        .join(Skill)
        .where(and_(
            UserSkill.skill_type == "teach",
            UserSkill.status == "active"
        ))
    )
    
    skills_data = []
    for user_skill, skill in result:
        skills_data.append({
            "skill_id": skill.id,
            "skill_name": skill.name,
            "category": skill.category,
            "proficiency": user_skill.proficiency_level,
            "available_hours": user_skill.available_hours
        })
    
    return {"skills": skills_data}

def get_skill_swap_intro(language: str) -> str:
    """Get skill swap introduction"""
    messages = {
        "hi": "स्किल-स्वैप में आप अपने कौशल सिखा सकती हैं और क्रेडिट कमा सकती हैं। फिर उन क्रेडिट से नए कौशल सीख सकती हैं। आप सिखाना चाहती हैं या सीखना?"
    }
    return messages.get(language, "Skill swap: teach to earn credits, use credits to learn")

def get_skill_error_message(language: str) -> str:
    """Get error message"""
    return {"hi": "स्किल-स्वैप में समस्या हुई। कृपया फिर से प्रयास करें।"}.get(language, "Error in skill swap")
