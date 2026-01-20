"""
Trace Builder Service

Automatically generates decision steps from decision data.
This is used when steps are not explicitly provided.
"""
from typing import List
from datetime import datetime, timedelta
from app.schemas import DecisionCreate, DecisionStepCreate, StepType


class TraceBuilder:
    """
    Builds structured decision traces from decision data
    
    Converts decision metadata into a sequence of human-readable steps.
    """
    
    def build_steps(self, decision: DecisionCreate) -> List[DecisionStepCreate]:
        """
        Generate decision steps from decision data
        
        Creates a logical sequence: Input → Reasoning → Decision → Action → Outcome
        """
        steps = []
        
        # Step 1: Input
        input_summary = self._summarize_input(decision.input_data)
        steps.append(DecisionStepCreate(
            step_type=StepType.INPUT,
            content=f"Input received: {input_summary}",
            step_metadata={"input_data": decision.input_data}
        ))
        
        # Step 2: Reasoning (if system state exists, include it)
        if decision.system_state:
            state_summary = self._summarize_state(decision.system_state)
            steps.append(DecisionStepCreate(
                step_type=StepType.REASONING,
                content=f"System state: {state_summary}",
                step_metadata={"system_state": decision.system_state}
            ))
        
        # Step 3: Reasoning - Main logic
        steps.append(DecisionStepCreate(
            step_type=StepType.REASONING,
            content=decision.reasoning,
            step_metadata={
                "source": decision.source.value,
                "confidence": decision.confidence
            }
        ))
        
        # Step 4: Decision
        decision_content = f"Decision: {decision.decision}"
        if decision.confidence < 0.7:
            decision_content += " (Low confidence - may require review)"
        
        steps.append(DecisionStepCreate(
            step_type=StepType.DECISION,
            content=decision_content,
            step_metadata={
                "decision": decision.decision,
                "confidence": decision.confidence,
                "source": decision.source.value
            }
        ))
        
        # Step 5: Action (implicit - what happens next)
        action_content = self._generate_action(decision)
        if action_content:
            steps.append(DecisionStepCreate(
                step_type=StepType.ACTION,
                content=action_content,
                step_metadata={"auto_generated": True}
            ))
        
        # Step 6: Outcome (if provided)
        if decision.outcome:
            steps.append(DecisionStepCreate(
                step_type=StepType.OUTCOME,
                content=decision.outcome,
                step_metadata=decision.outcome_data or {}
            ))
        
        return steps
    
    def _summarize_input(self, input_data: dict) -> str:
        """Create human-readable summary of input data"""
        if not input_data:
            return "No input data"
        
        # Try to create a natural language summary
        if len(input_data) == 1:
            key, value = list(input_data.items())[0]
            return f"{key} = {value}"
        
        summary_parts = []
        for key, value in list(input_data.items())[:3]:  # First 3 items
            summary_parts.append(f"{key}={value}")
        
        result = ", ".join(summary_parts)
        if len(input_data) > 3:
            result += f", +{len(input_data) - 3} more"
        
        return result
    
    def _summarize_state(self, system_state: dict) -> str:
        """Create human-readable summary of system state"""
        if not system_state:
            return "No state data"
        
        summary_parts = []
        for key, value in list(system_state.items())[:3]:
            summary_parts.append(f"{key}={value}")
        
        result = ", ".join(summary_parts)
        if len(system_state) > 3:
            result += f", +{len(system_state) - 3} more"
        
        return result
    
    def _generate_action(self, decision: DecisionCreate) -> str:
        """Generate action text based on decision"""
        # This is a simple heuristic - can be extended
        decision_text = decision.decision.lower()
        
        if "approve" in decision_text:
            return "Executing approval workflow"
        elif "reject" in decision_text or "deny" in decision_text:
            return "Executing rejection workflow"
        elif "escalate" in decision_text:
            return "Escalating to human review"
        elif "route" in decision_text:
            return "Routing to appropriate handler"
        else:
            return "Executing decision action"
