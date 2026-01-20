"""
Example: Integrating AI Decision Timeline with a Real AI System

This example shows how to integrate the decision timeline with:
1. OpenAI API for LLM-based decisions
2. Custom rule engine
3. Hybrid decision-making

This demonstrates how production AI systems can use the timeline for explainability.
"""
import os
from typing import Dict, Any, Tuple
from app.schemas import DecisionCreate, DecisionSource
from app.services.trace_builder import TraceBuilder
import requests

# Example: Simulated OpenAI integration (replace with actual API calls)
class AIDecisionSystem:
    """
    Example AI system that makes decisions and logs them to the timeline
    """
    
    def __init__(self, api_base_url: str = "http://localhost:8000/api"):
        self.api_base_url = api_base_url
        self.trace_builder = TraceBuilder()
        
        # Initialize decision rules
        self.rules = {
            "auto_approve_refund": {
                "conditions": {
                    "max_amount": 100.0,
                    "required_tier": "premium",
                    "max_refund_count": 2
                },
                "confidence": 0.95
            },
            "escalate_legal": {
                "keywords": ["legal", "lawsuit", "attorney", "fraud", "sue"],
                "confidence": 0.98
            }
        }
    
    def process_customer_request(
        self,
        request_type: str,
        user_data: Dict[str, Any],
        request_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process a customer request and create a decision trace
        
        This is the main entry point that would be called by your application.
        """
        # Step 1: Try rule-based decision first
        decision, source, confidence, reasoning = self._try_rule_based(
            request_type, user_data, request_data
        )
        
        # Step 2: If no rule matches, use LLM
        if decision is None:
            decision, source, confidence, reasoning = self._llm_decision(
                request_type, user_data, request_data
            )
        
        # Step 3: Create decision record
        decision_record = DecisionCreate(
            input_data={
                "request_type": request_type,
                **request_data
            },
            system_state={
                "user_tier": user_data.get("tier"),
                "account_age_days": user_data.get("account_age_days"),
                **user_data
            },
            reasoning=reasoning,
            decision=decision,
            confidence=confidence,
            source=source,
            tags=[request_type, source.value]
        )
        
        # Step 4: Log to timeline API
        response = self._log_decision(decision_record)
        
        return {
            "decision": decision,
            "confidence": confidence,
            "reasoning": reasoning,
            "decision_id": response.get("decision_id"),
            "timeline_url": f"{self.api_base_url}/decisions/{response.get('decision_id')}"
        }
    
    def _try_rule_based(
        self,
        request_type: str,
        user_data: Dict[str, Any],
        request_data: Dict[str, Any]
    ) -> Tuple[str, DecisionSource, float, str]:
        """
        Attempt to make decision using rules
        """
        # Rule: Auto-approve refunds
        if request_type == "refund":
            rule = self.rules["auto_approve_refund"]
            amount = request_data.get("amount", 0)
            
            if (
                user_data.get("tier") == rule["conditions"]["required_tier"] and
                amount <= rule["conditions"]["max_amount"] and
                user_data.get("refund_count", 0) <= rule["conditions"]["max_refund_count"]
            ):
                return (
                    "approve_refund",
                    DecisionSource.RULE,
                    rule["confidence"],
                    f"Auto-approved: Premium user, amount ${amount} within limit, low refund history"
                )
        
        # Rule: Escalate legal issues
        if request_type == "support_ticket":
            message = request_data.get("message", "").lower()
            rule = self.rules["escalate_legal"]
            
            if any(keyword in message for keyword in rule["keywords"]):
                return (
                    "escalate_to_legal",
                    DecisionSource.RULE,
                    rule["confidence"],
                    "Legal keywords detected. Escalating to legal team per compliance policy."
                )
        
        return None, None, None, None
    
    def _llm_decision(
        self,
        request_type: str,
        user_data: Dict[str, Any],
        request_data: Dict[str, Any]
    ) -> Tuple[str, DecisionSource, float, str]:
        """
        Use LLM to make decision when no rule matches
        
        In production, this would call OpenAI, Anthropic, etc.
        """
        # Example prompt for LLM
        prompt = f"""
        You are an AI customer service decision system.
        
        Request Type: {request_type}
        User Info: {user_data}
        Request Details: {request_data}
        
        Decide what action to take. Respond in JSON format:
        {{
            "decision": "action_to_take",
            "reasoning": "explanation",
            "confidence": 0.0-1.0
        }}
        
        Available actions: approve, reject, escalate_to_human, request_more_info
        """
        
        # Simulate LLM response (replace with actual API call)
        # response = openai.ChatCompletion.create(
        #     model="gpt-4",
        #     messages=[{"role": "user", "content": prompt}]
        # )
        
        # For this example, return a fallback decision
        return (
            "escalate_to_human",
            DecisionSource.LLM,
            0.75,
            f"No clear rule applies. LLM recommends human review for {request_type}."
        )
    
    def _log_decision(self, decision: DecisionCreate) -> Dict[str, Any]:
        """
        Log decision to the timeline API
        """
        try:
            response = requests.post(
                f"{self.api_base_url}/decisions",
                json=decision.dict()
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Failed to log decision: {e}")
            return {}


# Example Usage
if __name__ == "__main__":
    # Initialize the AI system
    ai_system = AIDecisionSystem()
    
    # Example 1: Refund request (rule-based)
    print("=" * 60)
    print("Example 1: Refund Request (Rule-Based Decision)")
    print("=" * 60)
    
    result = ai_system.process_customer_request(
        request_type="refund",
        user_data={
            "user_id": "user_12345",
            "tier": "premium",
            "account_age_days": 365,
            "refund_count": 1
        },
        request_data={
            "amount": 79.99,
            "reason": "Product not as described",
            "order_id": "ORD-8821"
        }
    )
    
    print(f"Decision: {result['decision']}")
    print(f"Confidence: {result['confidence']}")
    print(f"Reasoning: {result['reasoning']}")
    print(f"View in timeline: {result.get('timeline_url')}")
    print()
    
    # Example 2: Support ticket with legal keywords (rule-based)
    print("=" * 60)
    print("Example 2: Support Ticket (Legal Escalation)")
    print("=" * 60)
    
    result = ai_system.process_customer_request(
        request_type="support_ticket",
        user_data={
            "user_id": "user_67890",
            "tier": "standard",
            "account_age_days": 90
        },
        request_data={
            "message": "I want to speak with your legal department about privacy violations",
            "category": "complaint"
        }
    )
    
    print(f"Decision: {result['decision']}")
    print(f"Confidence: {result['confidence']}")
    print(f"Reasoning: {result['reasoning']}")
    print(f"View in timeline: {result.get('timeline_url')}")
    print()
    
    # Example 3: Edge case requiring LLM
    print("=" * 60)
    print("Example 3: Complex Case (LLM Decision)")
    print("=" * 60)
    
    result = ai_system.process_customer_request(
        request_type="account_modification",
        user_data={
            "user_id": "user_99999",
            "tier": "enterprise",
            "account_age_days": 1200
        },
        request_data={
            "requested_change": "Merge two enterprise accounts with different billing cycles",
            "urgency": "medium"
        }
    )
    
    print(f"Decision: {result['decision']}")
    print(f"Confidence: {result['confidence']}")
    print(f"Reasoning: {result['reasoning']}")
    print(f"View in timeline: {result.get('timeline_url')}")
    print()
    
    print("=" * 60)
    print("[OK] All decisions logged to timeline!")
    print("View them at: http://localhost:3000")
    print("=" * 60)
