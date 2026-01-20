"""
Trace endpoints

Handles querying and analyzing decision traces.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Dict, Any
from datetime import datetime, timedelta

from app.database import get_db
from app.models import Decision as DecisionModel, DecisionStep as StepModel, DecisionSource

router = APIRouter()


@router.get("/traces/stats")
async def get_trace_statistics(
    days: int = Query(default=7, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """
    Get statistics about decision traces
    
    Returns aggregate data for dashboards and analytics.
    """
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    # Total decisions
    total_decisions = db.query(func.count(DecisionModel.id)).filter(
        DecisionModel.timestamp >= cutoff_date
    ).scalar()
    
    # Decisions by source
    by_source = db.query(
        DecisionModel.source,
        func.count(DecisionModel.id).label("count")
    ).filter(
        DecisionModel.timestamp >= cutoff_date
    ).group_by(DecisionModel.source).all()
    
    # Average confidence
    avg_confidence = db.query(
        func.avg(DecisionModel.confidence)
    ).filter(
        DecisionModel.timestamp >= cutoff_date
    ).scalar()
    
    # Decisions with low confidence (<0.7)
    low_confidence_count = db.query(func.count(DecisionModel.id)).filter(
        DecisionModel.timestamp >= cutoff_date,
        DecisionModel.confidence < 0.7
    ).scalar()
    
    return {
        "period_days": days,
        "total_decisions": total_decisions or 0,
        "decisions_by_source": {item[0].value: item[1] for item in by_source},
        "average_confidence": round(float(avg_confidence or 0), 4),
        "low_confidence_count": low_confidence_count or 0,
        "low_confidence_percentage": round(
            (low_confidence_count or 0) / (total_decisions or 1) * 100, 2
        )
    }


@router.get("/traces/timeline")
async def get_timeline_data(
    days: int = Query(default=7, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """
    Get decision counts over time for timeline visualization
    
    Returns daily counts of decisions for charting.
    """
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    # Query decisions grouped by date
    results = db.query(
        func.date(DecisionModel.timestamp).label("date"),
        func.count(DecisionModel.id).label("count")
    ).filter(
        DecisionModel.timestamp >= cutoff_date
    ).group_by(
        func.date(DecisionModel.timestamp)
    ).order_by(
        func.date(DecisionModel.timestamp)
    ).all()
    
    return {
        "timeline": [
            {
                "date": str(item[0]),
                "count": item[1]
            }
            for item in results
        ]
    }


@router.get("/traces/search")
async def search_traces(
    query: str = Query(..., min_length=1),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Search decisions by content
    
    Searches across reasoning, decision text, and step content.
    """
    search_pattern = f"%{query}%"
    
    # Search in decision reasoning and decision text
    decisions = db.query(DecisionModel).filter(
        (DecisionModel.reasoning.ilike(search_pattern)) |
        (DecisionModel.decision.ilike(search_pattern))
    ).limit(limit).all()
    
    results = []
    for decision in decisions:
        results.append({
            "decision_id": decision.decision_id,
            "timestamp": decision.timestamp,
            "decision": decision.decision,
            "reasoning": decision.reasoning[:200] + "..." if len(decision.reasoning) > 200 else decision.reasoning,
            "confidence": decision.confidence,
            "source": decision.source.value
        })
    
    return {
        "query": query,
        "total_results": len(results),
        "results": results
    }


@router.get("/traces/tags")
async def get_all_tags(db: Session = Depends(get_db)):
    """
    Get all unique tags used in decisions
    
    Useful for filtering and categorization.
    """
    # Get all decisions with tags
    decisions = db.query(DecisionModel).filter(
        DecisionModel.tags.isnot(None)
    ).all()
    
    # Collect unique tags
    all_tags = set()
    for decision in decisions:
        if decision.tags:
            all_tags.update(decision.tags)
    
    return {
        "tags": sorted(list(all_tags)),
        "total_unique_tags": len(all_tags)
    }
