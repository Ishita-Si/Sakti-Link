"""Learning API Router"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import List, Optional
from edge_server.db.database import get_db_session
from edge_server.services import learning_service

router = APIRouter()

class ModuleListRequest(BaseModel):
    category: Optional[str] = None
    language: str = "hi"
    user_id: str

@router.post("/modules/list")
async def list_modules(request: ModuleListRequest, db: AsyncSession = Depends(get_db_session)):
    """List learning modules"""
    try:
        modules = await learning_service.suggest_modules(request.user_id, request.category or "financial_literacy", request.language, db)
        return {"success": True, "response": modules}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/modules/{module_id}/start")
async def start_module(module_id: int, user_id: str, db: AsyncSession = Depends(get_db_session)):
    """Start a learning module"""
    result = await learning_service.start_learning_module(user_id, module_id, db)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result.get("error"))
    return result

@router.post("/modules/{module_id}/complete")
async def complete_module(module_id: int, user_id: str, db: AsyncSession = Depends(get_db_session)):
    """Complete a learning module"""
    result = await learning_service.complete_learning_module(user_id, module_id, db)
    return result

@router.get("/credits/{user_id}")
async def get_credits(user_id: str, db: AsyncSession = Depends(get_db_session)):
    """Get user's credit balance"""
    credits = await learning_service.get_user_credits(user_id, db)
    return {"user_id": user_id, "credits": credits}
