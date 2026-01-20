"""
SQLAlchemy models for decision traces

Each decision is composed of:
- Metadata (ID, timestamp, confidence, source)
- Decision data (input, state, reasoning, decision, outcome)
- Steps (ordered sequence of decision stages)
"""
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, JSON, Text, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.database import Base


class DecisionSource(str, enum.Enum):
    """Source of the decision"""
    RULE = "rule"
    LLM = "llm"
    HYBRID = "hybrid"
    MANUAL = "manual"


class StepType(str, enum.Enum):
    """Types of decision steps"""
    INPUT = "input"
    REASONING = "reasoning"
    DECISION = "decision"
    ACTION = "action"
    OUTCOME = "outcome"


class Decision(Base):
    """
    Main decision record
    
    Represents a single AI decision with all its context, reasoning, and outcome.
    """
    __tablename__ = "decisions"
    
    id = Column(Integer, primary_key=True, index=True)
    decision_id = Column(String, unique=True, index=True, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Decision data
    input_data = Column(JSON, nullable=False)  # What triggered the decision
    system_state = Column(JSON, nullable=True)  # System context at decision time
    reasoning = Column(Text, nullable=False)  # Human-readable explanation
    decision = Column(String, nullable=False)  # The actual decision made
    confidence = Column(Float, nullable=False)  # 0.0 to 1.0
    source = Column(Enum(DecisionSource), nullable=False)
    
    # Outcome
    outcome = Column(String, nullable=True)  # Result of the decision
    outcome_data = Column(JSON, nullable=True)  # Additional outcome information
    
    # Metadata
    tags = Column(JSON, nullable=True)  # For categorization/filtering
    
    # Relationships
    steps = relationship("DecisionStep", back_populates="decision", cascade="all, delete-orphan", order_by="DecisionStep.step_order")
    
    def __repr__(self):
        return f"<Decision {self.decision_id} - {self.decision} ({self.confidence:.2f})>"


class DecisionStep(Base):
    """
    Individual step in a decision trace
    
    Steps form an ordered sequence showing how the decision unfolded.
    """
    __tablename__ = "decision_steps"
    
    id = Column(Integer, primary_key=True, index=True)
    decision_id = Column(Integer, ForeignKey("decisions.id"), nullable=False)
    
    step_order = Column(Integer, nullable=False)  # 0, 1, 2, 3...
    step_type = Column(Enum(StepType), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Step content
    content = Column(Text, nullable=False)  # Main text content
    step_metadata = Column(JSON, nullable=True)  # Additional data (e.g., rule matched, confidence)
    
    # Relationships
    decision = relationship("Decision", back_populates="steps")
    
    def __repr__(self):
        return f"<Step {self.step_order}: {self.step_type} - {self.content[:50]}>"
