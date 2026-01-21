"""Legal API Router"""
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from edge_server.db.database import get_db_session
from edge_server.services import legal_service

router = APIRouter()

class LegalQueryRequest(BaseModel):
    user_id: str
    query: str
    language: str = "hi"

@router.post("/query")
async def legal_query(request: Request, query_req: LegalQueryRequest, db: AsyncSession = Depends(get_db_session)):
    """Ask a legal question"""
    model_manager = request.app.state.model_manager
    response = await legal_service.handle_legal_intent(
        query_req.user_id,
        query_req.query,
        query_req.language,
        db,
        model_manager
    )
    return {"response": response}

@router.get("/topics")
async def get_legal_topics(language: str = "hi", db: AsyncSession = Depends(get_db_session)):
    """Get available legal topics"""
    topics = await legal_service.list_legal_topics(language, db)
    return topics
