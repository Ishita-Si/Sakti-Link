"""Skills API Router"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from edge_server.db.database import get_db_session
from edge_server.services import skill_service

router = APIRouter()

class RegisterTeachSkillRequest(BaseModel):
    user_id: str
    skill_name: str
    proficiency: int = 3
    
class RegisterLearnSkillRequest(BaseModel):
    user_id: str
    skill_id: int

@router.post("/teach")
async def register_teach_skill(request: RegisterTeachSkillRequest, db: AsyncSession = Depends(get_db_session)):
    """Register a skill to teach"""
    result = await skill_service.register_skill_to_teach(
        request.user_id,
        request.skill_name,
        request.proficiency,
        db
    )
    return result

@router.post("/learn")
async def register_learn_skill(request: RegisterLearnSkillRequest, db: AsyncSession = Depends(get_db_session)):
    """Register interest in learning a skill"""
    result = await skill_service.register_skill_to_learn(request.user_id, request.skill_id, db)
    return result

@router.get("/marketplace")
async def get_marketplace(language: str = "hi", db: AsyncSession = Depends(get_db_session)):
    """Get skill marketplace"""
    result = await skill_service.get_skill_marketplace(language, db)
    return result
