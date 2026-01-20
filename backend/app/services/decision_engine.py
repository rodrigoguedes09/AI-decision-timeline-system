"""
Decision Engine Service

Example service showing how to integrate decision-making logic with the trace system.
This demonstrates how real AI systems would use the timeline.
"""
from typing import Dict, Any, Tuple
from app.schemas import DecisionCreate, DecisionSource


class DecisionEngine:
    """
    Example decision engine that makes decisions and creates trace data
    
    In a real system, this would integrate with:
    - Rule engines
    - LLM APIs (OpenAI, Anthropic, etc.)
    - ML models
    - Business logic
    """
    
    def __init__(self):
        self.rules = self._load_rules()
    
    def _load_rules(self) -> Dict[str, Any]:
        """
        Load decision rules
        
        In production, this would come from a database or config file.
        """
        return {
            "refund_auto_approve": {
                "conditions": {
                    "user_tier": "premium",
                    "amount_max": 100.0,
                    "refund_count_max": 2
                },
                "confidence": 0.95
            },
            "support_escalation": {
                "conditions": {
                    "keywords": ["legal", "lawsuit", "attorney", "fraud"],
                    "urgency": "high"
                },
                "confidence": 0.98
            }
        }
    
    def make_decision(
        self,
        input_data: Dict[str, Any],
        system_state: Dict[str, Any]
    ) -> DecisionCreate:
        """
        Make a decision based on input and state
        
        Returns a DecisionCreate object ready to be stored.
        """
        # Try rule-based decision first
        decision, source, confidence, reasoning = self._try_rule_based(
            input_data, system_state
        )
        
        # If no rule matches, could call LLM here
        if decision is None:
            decision, source, confidence, reasoning = self._fallback_decision(
                input_data, system_state
            )
        
        return DecisionCreate(
            input_data=input_data,
            system_state=system_state,
            reasoning=reasoning,
            decision=decision,
            confidence=confidence,
            source=source,
            tags=self._generate_tags(input_data)
        )
    
    def _try_rule_based(
        self,
        input_data: Dict[str, Any],
        system_state: Dict[str, Any]
    ) -> Tuple[str, DecisionSource, float, str]:
        """
        Attempt to make decision using rules
        """
        # Example: Refund auto-approval
        if input_data.get("request_type") == "refund":
            rule = self.rules["refund_auto_approve"]
            conditions = rule["conditions"]
            
            if (
                system_state.get("user_tier") == conditions["user_tier"] and
                input_data.get("amount", 0) <= conditions["amount_max"] and
                system_state.get("refund_count", 0) <= conditions["refund_count_max"]
            ):
                return (
                    "approve_refund",
                    DecisionSource.RULE,
                    rule["confidence"],
                    f"Auto-approved: User is {conditions['user_tier']} tier with good history. "
                    f"Amount ${input_data.get('amount')} is within auto-approval limit."
                )
        
        # Example: Support escalation
        if input_data.get("request_type") == "support_ticket":
            message = input_data.get("message", "").lower()
            rule = self.rules["support_escalation"]
            
            if any(keyword in message for keyword in rule["conditions"]["keywords"]):
                return (
                    "escalate_to_human",
                    DecisionSource.RULE,
                    rule["confidence"],
                    f"Escalating to human agent: Message contains sensitive keywords requiring human review."
                )
        
        return None, None, None, None
    
    def _fallback_decision(
        self,
        input_data: Dict[str, Any],
        system_state: Dict[str, Any]
    ) -> Tuple[str, DecisionSource, float, str]:
        """
        Fallback decision when no rule matches
        
        In production, this would call an LLM or ML model.
        """
        return (
            "manual_review_required",
            DecisionSource.MANUAL,
            0.5,
            "No automatic decision rule matched. Routing to manual review queue."
        )
    
    def _generate_tags(self, input_data: Dict[str, Any]) -> list:
        """Generate tags for categorization"""
        tags = []
        
        if "request_type" in input_data:
            tags.append(input_data["request_type"])
        
        if "amount" in input_data:
            amount = input_data["amount"]
            if amount > 1000:
                tags.append("high_value")
            elif amount > 100:
                tags.append("medium_value")
            else:
                tags.append("low_value")
        
        return tags
