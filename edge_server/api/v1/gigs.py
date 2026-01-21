"""Gigs API Router"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from edge_server.db.database import get_db_session
from edge_server.services import gig_service

router = APIRouter()

@router.get("/available")
async def get_available_gigs(user_id: str, language: str = "hi", db: AsyncSession = Depends(get_db_session)):
    """Get available gigs"""
    gigs = await gig_service.get_available_gigs(user_id, language, db)
    return {"gigs": [{"id": g.id, "title": g.title, "payment": g.payment, "location": g.location} for g in gigs]}

@router.post("/{gig_id}/apply")
async def apply_for_gig(gig_id: int, user_id: str, db: AsyncSession = Depends(get_db_session)):
    """Apply for a gig"""
    result = await gig_service.apply_for_gig(user_id, gig_id, db)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@router.get("/user/{user_id}")
async def get_user_gigs(user_id: str, db: AsyncSession = Depends(get_db_session)):
    """Get user's gig applications"""
    apps = await gig_service.get_user_applications(user_id, db)
    return {"applications": [{"gig_id": a.gig_id, "status": a.status, "applied_at": a.applied_at} for a in apps]}
