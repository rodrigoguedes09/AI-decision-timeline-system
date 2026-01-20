"""
Pydantic schemas for request/response validation

Strong typing ensures data integrity and provides auto-generated API documentation.
"""
from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum


class DecisionSource(str, Enum):
    """Source of the decision"""
    RULE = "rule"
    LLM = "llm"
    HYBRID = "hybrid"
    MANUAL = "manual"


class StepType(str, Enum):
    """Types of decision steps"""
    INPUT = "input"
    REASONING = "reasoning"
    DECISION = "decision"
    ACTION = "action"
    OUTCOME = "outcome"


class DecisionStepBase(BaseModel):
    """Base schema for decision steps"""
    step_type: StepType
    content: str = Field(..., min_length=1, max_length=5000)
    step_metadata: Optional[Dict[str, Any]] = None


class DecisionStepCreate(DecisionStepBase):
    """Schema for creating a decision step"""
    pass


class DecisionStep(DecisionStepBase):
    """Schema for decision step response"""
    id: int
    step_order: int
    timestamp: datetime
    
    class Config:
        from_attributes = True


class DecisionBase(BaseModel):
    """Base schema for decisions"""
    input_data: Dict[str, Any] = Field(..., description="Input that triggered the decision")
    system_state: Optional[Dict[str, Any]] = Field(None, description="System context at decision time")
    reasoning: str = Field(..., min_length=1, max_length=5000, description="Human-readable explanation")
    decision: str = Field(..., min_length=1, max_length=200, description="The decision made")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score (0-1)")
    source: DecisionSource = Field(..., description="Source of the decision")
    outcome: Optional[str] = Field(None, max_length=500)
    outcome_data: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    
    @validator('confidence')
    def validate_confidence(cls, v):
        if not 0.0 <= v <= 1.0:
            raise ValueError('Confidence must be between 0.0 and 1.0')
        return round(v, 4)


class DecisionCreate(DecisionBase):
    """Schema for creating a decision"""
    steps: Optional[List[DecisionStepCreate]] = None


class Decision(DecisionBase):
    """Schema for decision response"""
    id: int
    decision_id: str
    timestamp: datetime
    steps: List[DecisionStep] = []
    
    class Config:
        from_attributes = True


class DecisionSummary(BaseModel):
    """Lightweight decision summary for timeline views"""
    id: int
    decision_id: str
    timestamp: datetime
    decision: str
    confidence: float
    source: DecisionSource
    outcome: Optional[str]
    tags: Optional[List[str]]
    step_count: int
    
    class Config:
        from_attributes = True


class DecisionReplay(BaseModel):
    """Schema for replaying a decision step-by-step"""
    decision: Decision
    total_steps: int
    duration_seconds: Optional[float] = None


class TimelineQuery(BaseModel):
    """Query parameters for timeline filtering"""
    limit: int = Field(default=50, ge=1, le=500)
    offset: int = Field(default=0, ge=0)
    source: Optional[DecisionSource] = None
    min_confidence: Optional[float] = Field(None, ge=0.0, le=1.0)
    tags: Optional[List[str]] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    sort_order: str = Field(default="desc", pattern="^(asc|desc)$")


class HealthCheck(BaseModel):
    """Health check response"""
    status: str
    service: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
