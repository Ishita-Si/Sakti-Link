"""System API Router"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from edge_server.db.database import get_db_session
from edge_server.core.config import settings
from edge_server.models.database import SystemMetrics
from sqlalchemy import select, func
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/status")
async def system_status():
    """Get system status"""
    return {
        "status": "operational",
        "mode": "offline" if settings.OFFLINE_MODE else "online",
        "version": settings.VERSION,
        "supported_languages": settings.SUPPORTED_LANGUAGES
    }

@router.get("/metrics")
async def get_metrics(db: AsyncSession = Depends(get_db_session)):
    """Get system metrics"""
    # Get metrics from last 24 hours
    yesterday = datetime.utcnow() - timedelta(days=1)
    
    result = await db.execute(
        select(
            SystemMetrics.metric_type,
            func.sum(SystemMetrics.metric_value).label("total"),
            func.count(SystemMetrics.id).label("count")
        )
        .where(SystemMetrics.timestamp >= yesterday)
        .group_by(SystemMetrics.metric_type)
    )
    
    metrics = {row.metric_type: {"total": row.total, "count": row.count} for row in result}
    
    return {
        "period": "24h",
        "metrics": metrics,
        "timestamp": datetime.utcnow().isoformat()
    }

@router.get("/sync/status")
async def sync_status():
    """Get synchronization status"""
    return {
        "enabled": settings.ENABLE_CLOUD_SYNC,
        "last_sync": None,  # Implement actual sync tracking
        "pending_syncs": 0,
        "cloud_url": settings.CLOUD_API_URL if settings.ENABLE_CLOUD_SYNC else None
    }

@router.post("/sync/trigger")
async def trigger_sync():
    """Manually trigger cloud sync"""
    if not settings.ENABLE_CLOUD_SYNC:
        return {"success": False, "message": "Cloud sync is disabled"}
    
    # Implement actual sync logic here
    return {"success": True, "message": "Sync initiated"}
