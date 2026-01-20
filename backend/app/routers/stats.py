"""
Statistics endpoints

Provides aggregated analytics and insights about decisions.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from datetime import datetime, timedelta

from app.database import get_db
from app.models import Decision as DecisionModel
from app.schemas import DecisionSource

router = APIRouter()


@router.get("/stats/overview")
async def get_stats_overview(
    days: int = Query(default=30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """
    Get overview statistics for the dashboard
    
    Returns aggregated metrics about decisions over the specified time period.
    """
    # Calculate date range
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Base query
    query = db.query(DecisionModel).filter(
        DecisionModel.timestamp >= start_date
    )
    
    # Total decisions
    total = query.count()
    
    # Average confidence
    avg_confidence = query.with_entities(
        func.avg(DecisionModel.confidence)
    ).scalar() or 0.0
    
    # Lowest confidence
    min_confidence = query.with_entities(
        func.min(DecisionModel.confidence)
    ).scalar() or 0.0
    
    # Source distribution
    source_distribution = {}
    for source in ['rule', 'llm', 'hybrid', 'manual']:
        count = query.filter(DecisionModel.source == source).count()
        if count > 0:
            source_distribution[source] = {
                "count": count,
                "percentage": round((count / total * 100) if total > 0 else 0, 2)
            }
    
    # Confidence ranges
    confidence_ranges = {
        "high": query.filter(DecisionModel.confidence >= 0.8).count(),
        "medium": query.filter(
            DecisionModel.confidence >= 0.5,
            DecisionModel.confidence < 0.8
        ).count(),
        "low": query.filter(DecisionModel.confidence < 0.5).count()
    }
    
    # Decisions per day (last 7 days for trend)
    daily_counts = []
    for i in range(6, -1, -1):
        day_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=i)
        day_end = day_start + timedelta(days=1)
        count = db.query(DecisionModel).filter(
            DecisionModel.timestamp >= day_start,
            DecisionModel.timestamp < day_end
        ).count()
        daily_counts.append({
            "date": day_start.strftime("%Y-%m-%d"),
            "count": count
        })
    
    return {
        "period_days": days,
        "total_decisions": total,
        "average_confidence": round(avg_confidence, 3),
        "lowest_confidence": round(min_confidence, 3),
        "source_distribution": source_distribution,
        "confidence_ranges": confidence_ranges,
        "daily_trend": daily_counts
    }


@router.get("/stats/timeline")
async def get_stats_timeline(
    days: int = Query(default=30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """
    Get time-series data for charts
    
    Returns daily aggregated data for visualization.
    """
    start_date = datetime.utcnow() - timedelta(days=days)
    
    timeline_data = []
    for i in range(days - 1, -1, -1):
        day_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=i)
        day_end = day_start + timedelta(days=1)
        
        day_query = db.query(DecisionModel).filter(
            DecisionModel.timestamp >= day_start,
            DecisionModel.timestamp < day_end
        )
        
        count = day_query.count()
        avg_conf = day_query.with_entities(
            func.avg(DecisionModel.confidence)
        ).scalar() or 0.0
        
        timeline_data.append({
            "date": day_start.strftime("%Y-%m-%d"),
            "count": count,
            "average_confidence": round(avg_conf, 3)
        })
    
    return {
        "period_days": days,
        "data": timeline_data
    }
