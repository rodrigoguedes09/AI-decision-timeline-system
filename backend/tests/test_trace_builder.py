"""
Tests for the trace builder service
"""
import pytest
from app.services.trace_builder import TraceBuilder
from app.schemas import DecisionCreate, DecisionSource, StepType


def test_build_steps_basic():
    """Test building steps from basic decision data"""
    builder = TraceBuilder()
    
    decision = DecisionCreate(
        input_data={"user_id": "123", "amount": 50.0},
        system_state={"user_tier": "premium"},
        reasoning="User meets criteria",
        decision="approve",
        confidence=0.9,
        source=DecisionSource.RULE
    )
    
    steps = builder.build_steps(decision)
    
    assert len(steps) > 0
    assert steps[0].step_type == StepType.INPUT
    assert any(s.step_type == StepType.REASONING for s in steps)
    assert any(s.step_type == StepType.DECISION for s in steps)


def test_build_steps_with_outcome():
    """Test building steps with outcome"""
    builder = TraceBuilder()
    
    decision = DecisionCreate(
        input_data={"test": "data"},
        reasoning="Test reasoning",
        decision="test_decision",
        confidence=0.85,
        source=DecisionSource.HYBRID,
        outcome="Test outcome"
    )
    
    steps = builder.build_steps(decision)
    
    # Should include outcome step
    assert any(s.step_type == StepType.OUTCOME for s in steps)
    outcome_step = [s for s in steps if s.step_type == StepType.OUTCOME][0]
    assert outcome_step.content == "Test outcome"


def test_summarize_input():
    """Test input summarization"""
    builder = TraceBuilder()
    
    # Simple input
    summary = builder._summarize_input({"key": "value"})
    assert "key" in summary
    
    # Complex input
    complex_input = {f"key{i}": f"value{i}" for i in range(5)}
    summary = builder._summarize_input(complex_input)
    assert "more" in summary.lower()  # Should indicate truncation
