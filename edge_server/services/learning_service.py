"""
Learning Service - Handles nano-learning modules and progress tracking
"""

from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from loguru import logger
from datetime import datetime

from edge_server.models.database import (
    User, LearningModule, LearningProgress, CreditTransaction
)
from edge_server.core.config import settings


async def handle_learning_intent(
    user_id: str,
    transcript: str,
    language: str,
    db: AsyncSession
) -> str:
    """
    Handle learning-related intents
    
    Args:
        user_id: User ID
        transcript: User's spoken text
        language: Language code
        db: Database session
    
    Returns:
        Response text
    """
    try:
        # Check user's credits
        credits = await get_user_credits(user_id, db)
        
        # Analyze what user wants to learn
        if "financial" in transcript.lower() or "वित्तीय" in transcript or "पैसा" in transcript:
            category = "financial_literacy"
            response = await suggest_modules(user_id, category, language, db)
        elif "digital" in transcript.lower() or "डिजिटल" in transcript:
            category = "digital_safety"
            response = await suggest_modules(user_id, category, language, db)
        elif "skill" in transcript.lower() or "कौशल" in transcript:
            category = "vocational_skills"
            response = await suggest_modules(user_id, category, language, db)
        else:
            # General learning inquiry
            response = await get_learning_overview(user_id, credits, language, db)
        
        return response
        
    except Exception as e:
        logger.error(f"Learning intent handling error: {e}")
        return get_error_message(language)


async def get_user_credits(user_id: str, db: AsyncSession) -> int:
    """Get user's current credit balance"""
    result = await db.execute(
        select(CreditTransaction)
        .where(CreditTransaction.user_id == user_id)
    )
    transactions = result.scalars().all()
    
    total_credits = sum(t.amount for t in transactions)
    return total_credits


async def suggest_modules(
    user_id: str,
    category: str,
    language: str,
    db: AsyncSession
) -> str:
    """Suggest learning modules in a category"""
    
    # Get available modules
    result = await db.execute(
        select(LearningModule)
        .where(
            and_(
                LearningModule.category == category,
                LearningModule.language == language,
                LearningModule.is_active == True
            )
        )
        .limit(3)
    )
    modules = result.scalars().all()
    
    if not modules:
        return get_no_modules_message(category, language)
    
    # Get user's progress for these modules
    module_ids = [m.id for m in modules]
    progress_result = await db.execute(
        select(LearningProgress)
        .where(
            and_(
                LearningProgress.user_id == user_id,
                LearningProgress.module_id.in_(module_ids)
            )
        )
    )
    progress_map = {p.module_id: p for p in progress_result.scalars().all()}
    
    # Build response
    response_parts = [get_category_intro(category, language)]
    
    for module in modules:
        progress = progress_map.get(module.id)
        status = progress.status if progress else "not_started"
        
        if status == "completed":
            continue  # Skip completed modules
        
        module_info = f"{module.title}"
        if module.duration:
            minutes = module.duration // 60
            module_info += f" - {minutes} मिनट"
        if module.credit_cost:
            module_info += f" - {module.credit_cost} क्रेडिट"
        
        response_parts.append(module_info)
    
    response_parts.append("कौनसा मॉड्यूल शुरू करना चाहेंगी?")
    
    return " । ".join(response_parts)


async def get_learning_overview(
    user_id: str,
    credits: int,
    language: str,
    db: AsyncSession
) -> str:
    """Get overview of learning progress"""
    
    # Get user's progress
    result = await db.execute(
        select(LearningProgress)
        .where(LearningProgress.user_id == user_id)
    )
    all_progress = result.scalars().all()
    
    completed = sum(1 for p in all_progress if p.status == "completed")
    in_progress = sum(1 for p in all_progress if p.status == "in_progress")
    
    messages = {
        "hi": f"आपके पास {credits} क्रेडिट हैं। आपने {completed} मॉड्यूल पूरे किए हैं और {in_progress} चल रहे हैं। आप वित्तीय साक्षरता, डिजिटल सुरक्षा, या व्यावसायिक कौशल के बारे में सीख सकती हैं। आप क्या सीखना चाहेंगी?"
    }
    
    return messages.get(language, messages["hi"])


async def start_learning_module(
    user_id: str,
    module_id: int,
    db: AsyncSession
) -> Dict[str, Any]:
    """Start a learning module"""
    
    # Check if user has enough credits
    credits = await get_user_credits(user_id, db)
    
    # Get module
    result = await db.execute(
        select(LearningModule).where(LearningModule.id == module_id)
    )
    module = result.scalar_one_or_none()
    
    if not module:
        return {"success": False, "error": "Module not found"}
    
    if credits < module.credit_cost:
        return {
            "success": False,
            "error": "Insufficient credits",
            "required": module.credit_cost,
            "available": credits
        }
    
    # Deduct credits
    transaction = CreditTransaction(
        user_id=user_id,
        amount=-module.credit_cost,
        transaction_type="learn",
        description=f"Started module: {module.title}",
        related_module_id=module_id
    )
    db.add(transaction)
    
    # Create or update progress
    progress_result = await db.execute(
        select(LearningProgress).where(
            and_(
                LearningProgress.user_id == user_id,
                LearningProgress.module_id == module_id
            )
        )
    )
    progress = progress_result.scalar_one_or_none()
    
    if not progress:
        progress = LearningProgress(
            user_id=user_id,
            module_id=module_id,
            status="in_progress",
            started_at=datetime.utcnow()
        )
        db.add(progress)
    else:
        progress.status = "in_progress"
        progress.started_at = datetime.utcnow()
    
    await db.commit()
    
    return {
        "success": True,
        "module": {
            "id": module.id,
            "title": module.title,
            "duration": module.duration,
            "audio_path": module.audio_path,
            "transcript": module.transcript
        }
    }


async def complete_learning_module(
    user_id: str,
    module_id: int,
    db: AsyncSession
) -> Dict[str, Any]:
    """Mark a learning module as complete"""
    
    # Get progress
    result = await db.execute(
        select(LearningProgress).where(
            and_(
                LearningProgress.user_id == user_id,
                LearningProgress.module_id == module_id
            )
        )
    )
    progress = result.scalar_one_or_none()
    
    if not progress:
        return {"success": False, "error": "Progress not found"}
    
    # Mark as completed
    progress.status = "completed"
    progress.completed_at = datetime.utcnow()
    progress.progress_percentage = 100.0
    
    # Award completion bonus (optional)
    bonus = 2  # Bonus credits for completion
    if bonus > 0:
        transaction = CreditTransaction(
            user_id=user_id,
            amount=bonus,
            transaction_type="bonus",
            description=f"Completed module: {module_id}",
            related_module_id=module_id
        )
        db.add(transaction)
        progress.credits_earned = bonus
    
    await db.commit()
    
    return {
        "success": True,
        "credits_earned": bonus,
        "message": "Module completed successfully"
    }


def get_category_intro(category: str, language: str) -> str:
    """Get category introduction"""
    intros = {
        "financial_literacy": {
            "hi": "वित्तीय साक्षरता के ये मॉड्यूल उपलब्ध हैं"
        },
        "digital_safety": {
            "hi": "डिजिटल सुरक्षा के ये मॉड्यूल उपलब्ध हैं"
        },
        "vocational_skills": {
            "hi": "व्यावसायिक कौशल के ये मॉड्यूल उपलब्ध हैं"
        }
    }
    return intros.get(category, {}).get(language, "")


def get_no_modules_message(category: str, language: str) -> str:
    """Get message when no modules available"""
    messages = {
        "hi": "इस श्रेणी में कोई मॉड्यूल उपलब्ध नहीं है। कृपया बाद में प्रयास करें।"
    }
    return messages.get(language, messages["hi"])


def get_error_message(language: str) -> str:
    """Get error message"""
    messages = {
        "hi": "मुझे खेद है, कुछ गड़बड़ हो गई। कृपया फिर से प्रयास करें।"
    }
    return messages.get(language, messages["hi"])
