"""
Decision endpoints

Handles creating, retrieving, and querying decision records.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import uuid
import csv
import io
import json

from app.database import get_db
from app.models import Decision as DecisionModel, DecisionStep as StepModel
from app.schemas import Decision, DecisionCreate, DecisionSummary, DecisionReplay, DecisionSource
from app.services.trace_builder import TraceBuilder

router = APIRouter()


@router.post("/decisions", response_model=Decision, status_code=201)
async def create_decision(
    decision: DecisionCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new decision record
    
    Accepts decision data and optional steps. If steps are not provided,
    they will be auto-generated based on the decision data.
    """
    # Generate unique decision ID
    decision_id = f"dec_{uuid.uuid4().hex[:12]}"
    
    # Create decision record
    db_decision = DecisionModel(
        decision_id=decision_id,
        input_data=decision.input_data,
        system_state=decision.system_state,
        reasoning=decision.reasoning,
        decision=decision.decision,
        confidence=decision.confidence,
        source=decision.source,
        outcome=decision.outcome,
        outcome_data=decision.outcome_data,
        tags=decision.tags
    )
    
    db.add(db_decision)
    db.flush()  # Get the ID without committing
    
    # Create steps
    if decision.steps:
        # Use provided steps
        for idx, step in enumerate(decision.steps):
            db_step = StepModel(
                decision_id=db_decision.id,
                step_order=idx,
                step_type=step.step_type,
                content=step.content,
                step_metadata=step.step_metadata
            )
            db.add(db_step)
    else:
        # Auto-generate steps from decision data
        trace_builder = TraceBuilder()
        steps = trace_builder.build_steps(decision)
        for idx, step in enumerate(steps):
            db_step = StepModel(
                decision_id=db_decision.id,
                step_order=idx,
                step_type=step.step_type,
                content=step.content,
                step_metadata=step.step_metadata
            )
            db.add(db_step)
    
    db.commit()
    db.refresh(db_decision)
    
    return db_decision


@router.get("/decisions", response_model=dict)
async def get_decisions(
    limit: int = Query(default=50, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    source: Optional[DecisionSource] = None,
    min_confidence: Optional[float] = Query(None, ge=0.0, le=1.0),
    max_confidence: Optional[float] = Query(None, ge=0.0, le=1.0),
    tag: Optional[str] = None,
    search: Optional[str] = None,
    sort: str = Query(default="desc", pattern="^(asc|desc)$"),
    db: Session = Depends(get_db)
):
    """
    Get timeline of decisions with optional filtering and pagination
    
    Returns lightweight summaries for efficient timeline rendering.
    Now includes total count for proper pagination UI.
    """
    query = db.query(DecisionModel)
    
    # Apply filters
    if source:
        query = query.filter(DecisionModel.source == source)
    
    if min_confidence is not None:
        query = query.filter(DecisionModel.confidence >= min_confidence)
    
    if max_confidence is not None:
        query = query.filter(DecisionModel.confidence <= max_confidence)
    
    if tag:
        query = query.filter(DecisionModel.tags.contains([tag]))
    
    # Search functionality (reasoning, decision, outcome)
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (DecisionModel.reasoning.ilike(search_term)) |
            (DecisionModel.decision.ilike(search_term)) |
            (DecisionModel.outcome.ilike(search_term))
        )
    
    # Get total count before pagination
    total = query.count()
    
    # Sort
    if sort == "desc":
        query = query.order_by(DecisionModel.timestamp.desc())
    else:
        query = query.order_by(DecisionModel.timestamp.asc())
    
    # Paginate
    decisions = query.offset(offset).limit(limit).all()
    
    # Convert to summaries
    summaries = []
    for decision in decisions:
        summaries.append(DecisionSummary(
            id=decision.id,
            decision_id=decision.decision_id,
            timestamp=decision.timestamp,
            decision=decision.decision,
            confidence=decision.confidence,
            source=decision.source,
            outcome=decision.outcome,
            tags=decision.tags,
            step_count=len(decision.steps)
        ))
    
    return {
        "decisions": summaries,
        "total": total,
        "limit": limit,
        "offset": offset,
        "has_more": offset + limit < total
    }


@router.get("/decisions/{decision_id}", response_model=Decision)
async def get_decision(
    decision_id: str,
    db: Session = Depends(get_db)
):
    """
    Get full details of a specific decision
    """
    decision = db.query(DecisionModel).filter(
        DecisionModel.decision_id == decision_id
    ).first()
    
    if not decision:
        raise HTTPException(status_code=404, detail="Decision not found")
    
    return decision


@router.get("/decisions/{decision_id}/replay", response_model=DecisionReplay)
async def replay_decision(
    decision_id: str,
    db: Session = Depends(get_db)
):
    """
    Get decision data optimized for replay mode
    
    This endpoint structures the data for step-by-step playback.
    """
    decision = db.query(DecisionModel).filter(
        DecisionModel.decision_id == decision_id
    ).first()
    
    if not decision:
        raise HTTPException(status_code=404, detail="Decision not found")
    
    # Calculate duration
    duration = None
    if decision.steps:
        first_step = min(decision.steps, key=lambda s: s.timestamp)
        last_step = max(decision.steps, key=lambda s: s.timestamp)
        duration = (last_step.timestamp - first_step.timestamp).total_seconds()
    
    return DecisionReplay(
        decision=decision,
        total_steps=len(decision.steps),
        duration_seconds=duration
    )


@router.delete("/decisions/{decision_id}", status_code=204)
async def delete_decision(
    decision_id: str,
    db: Session = Depends(get_db)
):
    """
    Delete a decision and all its steps
    """
    decision = db.query(DecisionModel).filter(
        DecisionModel.decision_id == decision_id
    ).first()
    
    if not decision:
        raise HTTPException(status_code=404, detail="Decision not found")
    
    db.delete(decision)
    db.commit()
    
    return None


@router.get("/decisions/export/csv")
async def export_decisions_csv(
    source: Optional[DecisionSource] = None,
    min_confidence: Optional[float] = Query(None, ge=0.0, le=1.0),
    db: Session = Depends(get_db)
):
    """
    Export decisions to CSV format
    """
    query = db.query(DecisionModel)
    
    if source:
        query = query.filter(DecisionModel.source == source)
    if min_confidence is not None:
        query = query.filter(DecisionModel.confidence >= min_confidence)
    
    decisions = query.order_by(DecisionModel.timestamp.desc()).all()
    
    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        'Decision ID', 'Timestamp', 'Decision', 'Confidence', 
        'Source', 'Reasoning', 'Outcome', 'Tags'
    ])
    
    # Write data
    for decision in decisions:
        writer.writerow([
            decision.decision_id,
            decision.timestamp.isoformat(),
            decision.decision,
            decision.confidence,
            decision.source,
            decision.reasoning or '',
            decision.outcome or '',
            ','.join(decision.tags) if decision.tags else ''
        ])
    
    output.seek(0)
    
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=decisions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"}
    )


@router.get("/decisions/export/json")
async def export_decisions_json(
    source: Optional[DecisionSource] = None,
    min_confidence: Optional[float] = Query(None, ge=0.0, le=1.0),
    db: Session = Depends(get_db)
):
    """
    Export decisions to JSON format
    """
    query = db.query(DecisionModel)
    
    if source:
        query = query.filter(DecisionModel.source == source)
    if min_confidence is not None:
        query = query.filter(DecisionModel.confidence >= min_confidence)
    
    decisions = query.order_by(DecisionModel.timestamp.desc()).all()
    
    # Convert to dict
    export_data = {
        "export_date": datetime.now().isoformat(),
        "total_decisions": len(decisions),
        "decisions": [
            {
                "decision_id": d.decision_id,
                "timestamp": d.timestamp.isoformat(),
                "input_data": d.input_data,
                "system_state": d.system_state,
                "reasoning": d.reasoning,
                "decision": d.decision,
                "confidence": d.confidence,
                "source": d.source,
                "outcome": d.outcome,
                "outcome_data": d.outcome_data,
                "tags": d.tags,
                "steps": [
                    {
                        "step_order": s.step_order,
                        "step_type": s.step_type,
                        "content": s.content,
                        "timestamp": s.timestamp.isoformat(),
                        "metadata": s.step_metadata
                    } for s in sorted(d.steps, key=lambda x: x.step_order)
                ]
            } for d in decisions
        ]
    }
    
    return StreamingResponse(
        iter([json.dumps(export_data, indent=2)]),
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename=decisions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"}
    )
