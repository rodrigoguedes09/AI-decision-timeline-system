"""
Load Demo Data

Populates the database with realistic decision scenarios.
This makes the system immediately usable and demonstrates its capabilities.
"""
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from datetime import datetime, timedelta
from app.database import SessionLocal, engine, Base
from app.models import Decision, DecisionStep, DecisionSource, StepType
import uuid
import random


def create_demo_decisions():
    """Create realistic demo decision scenarios"""
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    # Clear existing data
    db.query(DecisionStep).delete()
    db.query(Decision).delete()
    db.commit()
    
    print("Loading demo data...")
    
    # Scenario 1: Approved refund request
    create_refund_approval(db, minutes_ago=10)
    
    # Scenario 2: Rejected refund (over limit)
    create_refund_rejection(db, minutes_ago=25)
    
    # Scenario 3: Support ticket escalation
    create_support_escalation(db, minutes_ago=45)
    
    # Scenario 4: Low confidence - manual review
    create_manual_review(db, minutes_ago=60)
    
    # Scenario 5: Automated content moderation
    create_content_moderation(db, minutes_ago=90)
    
    # Scenario 6: Loan approval (hybrid decision)
    create_loan_approval(db, minutes_ago=120)
    
    # Add some older decisions for timeline variety
    for i in range(10):
        minutes = random.randint(180, 2880)  # 3 hours to 2 days ago
        if random.random() > 0.5:
            create_refund_approval(db, minutes_ago=minutes, silent=True)
        else:
            create_support_escalation(db, minutes_ago=minutes, silent=True)
    
    db.close()
    
    print("Demo data loaded successfully!")
    print(f"Created {6 + 10} decision records")
    print("\nStart the backend and visit http://localhost:8000/docs to explore the API")


def create_refund_approval(db, minutes_ago=0, silent=False):
    """Premium customer refund - auto-approved"""
    base_time = datetime.utcnow() - timedelta(minutes=minutes_ago)
    
    decision = Decision(
        decision_id=f"dec_{uuid.uuid4().hex[:12]}",
        timestamp=base_time,
        input_data={
            "request_type": "refund",
            "user_id": "user_12345",
            "amount": 79.99,
            "reason": "Product not as described"
        },
        system_state={
            "user_tier": "premium",
            "account_age_days": 456,
            "previous_refunds": 1,
            "total_spend": 2450.00
        },
        reasoning="User is premium tier with excellent history. Amount $79.99 is within auto-approval limit of $100. Previous refund count (1) is acceptable.",
        decision="approve_refund",
        confidence=0.95,
        source=DecisionSource.RULE,
        outcome="Refund processed successfully",
        tags=["refund", "auto_approved", "low_value"]
    )
    
    db.add(decision)
    db.flush()
    
    steps = [
        (0, StepType.INPUT, "Refund request received: $79.99 for order #ORD-8821", 
         {"order_id": "ORD-8821"}),
        (1, StepType.REASONING, "Checking user tier and account status...", 
         {"rule": "refund_eligibility_check"}),
        (2, StepType.REASONING, "User is premium tier with 456-day account age. Previous refunds: 1. Total lifetime spend: $2,450.00",
         {"user_tier": "premium", "risk_score": "low"}),
        (3, StepType.DECISION, "Decision: Approve refund automatically",
         {"confidence": 0.95, "source": "rule"}),
        (4, StepType.ACTION, "Processing refund to original payment method",
         {"payment_method": "Visa ending in 1234"}),
        (5, StepType.OUTCOME, "Refund processed successfully. Transaction ID: TXN-REF-9821",
         {"transaction_id": "TXN-REF-9821", "processing_time_ms": 234})
    ]
    
    for order, step_type, content, metadata in steps:
        step = DecisionStep(
            decision_id=decision.id,
            step_order=order,
            step_type=step_type,
            content=content,
            metadata=metadata,
            timestamp=base_time + timedelta(seconds=order)
        )
        db.add(step)
    
    db.commit()
    
    if not silent:
        print(f"[APPROVED] Created: Refund approval ({decision.decision_id})")


def create_refund_rejection(db, minutes_ago=0):
    """Non-premium customer over limit - rejected"""
    base_time = datetime.utcnow() - timedelta(minutes=minutes_ago)
    
    decision = Decision(
        decision_id=f"dec_{uuid.uuid4().hex[:12]}",
        timestamp=base_time,
        input_data={
            "request_type": "refund",
            "user_id": "user_67890",
            "amount": 249.99,
            "reason": "Changed my mind"
        },
        system_state={
            "user_tier": "standard",
            "account_age_days": 45,
            "previous_refunds": 3,
            "total_spend": 310.00
        },
        reasoning="User is standard tier with high refund rate (3 previous refunds). Amount $249.99 exceeds auto-approval limit for standard users ($50). Account age is only 45 days.",
        decision="reject_refund_auto_review",
        confidence=0.88,
        source=DecisionSource.RULE,
        outcome="Refund rejected - sent to manual review queue",
        tags=["refund", "rejected", "high_value"]
    )
    
    db.add(decision)
    db.flush()
    
    steps = [
        (0, StepType.INPUT, "Refund request received: $249.99 for order #ORD-3341",
         {"order_id": "ORD-3341"}),
        (1, StepType.REASONING, "Checking user tier and refund history...",
         {"rule": "refund_eligibility_check"}),
        (2, StepType.REASONING, "Risk factors detected: 3 previous refunds, account age 45 days, amount exceeds standard tier limit",
         {"risk_score": "high", "refund_rate": 0.75}),
        (3, StepType.DECISION, "Decision: Reject automatic refund - requires review",
         {"confidence": 0.88, "source": "rule", "reason": "exceeds_limits"}),
        (4, StepType.ACTION, "Adding to manual review queue with priority: normal",
         {"queue": "refund_review", "priority": "normal"}),
        (5, StepType.OUTCOME, "Request queued for human review. Estimated review time: 24-48 hours",
         {"queue_position": 12})
    ]
    
    for order, step_type, content, metadata in steps:
        step = DecisionStep(
            decision_id=decision.id,
            step_order=order,
            step_type=step_type,
            content=content,
            metadata=metadata,
            timestamp=base_time + timedelta(seconds=order * 2)
        )
        db.add(step)
    
    db.commit()
    
    print(f"[REJECTED] Created: Refund rejection ({decision.decision_id})")


def create_support_escalation(db, minutes_ago=0, silent=False):
    """Support ticket with legal keywords - escalated"""
    base_time = datetime.utcnow() - timedelta(minutes=minutes_ago)
    
    decision = Decision(
        decision_id=f"dec_{uuid.uuid4().hex[:12]}",
        timestamp=base_time,
        input_data={
            "request_type": "support_ticket",
            "user_id": "user_44321",
            "message": "I need to speak with your legal department about privacy concerns",
            "category": "account_issue"
        },
        system_state={
            "user_tier": "premium",
            "account_status": "active",
            "previous_tickets": 2
        },
        reasoning="Message contains sensitive keyword 'legal' requiring immediate human escalation per compliance policy.",
        decision="escalate_to_human_urgent",
        confidence=0.98,
        source=DecisionSource.RULE,
        outcome="Escalated to senior support agent",
        tags=["support", "escalated", "legal", "urgent"]
    )
    
    db.add(decision)
    db.flush()
    
    steps = [
        (0, StepType.INPUT, "Support ticket received: Category=account_issue",
         {"ticket_id": "TKT-9921"}),
        (1, StepType.REASONING, "Analyzing message content for keywords and sentiment...",
         {"sentiment": "neutral", "language": "en"}),
        (2, StepType.REASONING, "ALERT: Sensitive keyword detected: 'legal'. Policy requires immediate escalation.",
         {"matched_keywords": ["legal"], "policy": "compliance_escalation"}),
        (3, StepType.DECISION, "Decision: Escalate to human agent (URGENT priority)",
         {"confidence": 0.98, "source": "rule", "priority": "urgent"}),
        (4, StepType.ACTION, "Routing to senior support team",
         {"team": "senior_support", "agent_available": True}),
        (5, StepType.OUTCOME, "Ticket assigned to Agent Sarah Chen (available)",
         {"agent_id": "agent_sarah_chen", "response_time_target": "15_minutes"})
    ]
    
    for order, step_type, content, metadata in steps:
        step = DecisionStep(
            decision_id=decision.id,
            step_order=order,
            step_type=step_type,
            content=content,
            metadata=metadata,
            timestamp=base_time + timedelta(seconds=order)
        )
        db.add(step)
    
    db.commit()
    
    if not silent:
        print(f"[ESCALATED] Created: Support escalation ({decision.decision_id})")


def create_manual_review(db, minutes_ago=0):
    """Edge case requiring manual review"""
    base_time = datetime.utcnow() - timedelta(minutes=minutes_ago)
    
    decision = Decision(
        decision_id=f"dec_{uuid.uuid4().hex[:12]}",
        timestamp=base_time,
        input_data={
            "request_type": "account_closure",
            "user_id": "user_99887",
            "reason": "Moving to competitor"
        },
        system_state={
            "user_tier": "enterprise",
            "contract_value": 50000.00,
            "contract_end_date": "2026-06-30"
        },
        reasoning="Enterprise account with active contract. No automatic decision rule exists for mid-contract cancellations. Requires human negotiation.",
        decision="manual_review_required",
        confidence=0.50,
        source=DecisionSource.MANUAL,
        outcome="Pending manual review",
        tags=["account_management", "enterprise", "manual_review"]
    )
    
    db.add(decision)
    db.flush()
    
    steps = [
        (0, StepType.INPUT, "Account closure request: Enterprise account (Contract value: $50,000)",
         {"contract_id": "CNT-2024-E-0892"}),
        (1, StepType.REASONING, "Checking account status and contract terms...",
         {}),
        (2, StepType.REASONING, "Contract is active until 2026-06-30. Early termination clause requires approval.",
         {"contract_status": "active", "early_termination_penalty": 15000.00}),
        (3, StepType.DECISION, "Decision: Manual review required (No automatic rule applies)",
         {"confidence": 0.50, "source": "manual", "reason": "enterprise_contract"}),
        (4, StepType.ACTION, "Assigning to account management team",
         {"team": "enterprise_accounts", "priority": "high"}),
        (5, StepType.OUTCOME, "Pending review by Account Manager",
         {"assigned_to": "Jennifer Park", "follow_up_required": True})
    ]
    
    for order, step_type, content, metadata in steps:
        step = DecisionStep(
            decision_id=decision.id,
            step_order=order,
            step_type=step_type,
            content=content,
            metadata=metadata,
            timestamp=base_time + timedelta(seconds=order * 3)
        )
        db.add(step)
    
    db.commit()
    
    print(f"[MANUAL REVIEW] Created: Manual review ({decision.decision_id})")


def create_content_moderation(db, minutes_ago=0):
    """Automated content moderation"""
    base_time = datetime.utcnow() - timedelta(minutes=minutes_ago)
    
    decision = Decision(
        decision_id=f"dec_{uuid.uuid4().hex[:12]}",
        timestamp=base_time,
        input_data={
            "content_type": "user_comment",
            "content_id": "cmt_445566",
            "text": "Check out this amazing deal at example-spam-site.com/offer"
        },
        system_state={
            "user_reputation": 45,
            "account_age_days": 2,
            "previous_violations": 0
        },
        reasoning="LLM detected promotional content with external link. New account with low reputation score. Content classified as spam with 89% confidence.",
        decision="remove_content",
        confidence=0.89,
        source=DecisionSource.HYBRID,
        outcome="Content removed and user notified",
        tags=["moderation", "spam", "automated"]
    )
    
    db.add(decision)
    db.flush()
    
    steps = [
        (0, StepType.INPUT, "New comment posted by user_77123",
         {"content_id": "cmt_445566", "length": 67}),
        (1, StepType.REASONING, "Running content analysis (LLM + rules)...",
         {"model": "gpt-4-mini", "rule_engine": "v2.1"}),
        (2, StepType.REASONING, "LLM classification: Spam (89% confidence). Contains promotional link. Account age: 2 days.",
         {"spam_score": 0.89, "promotional_link": True, "risk_level": "medium"}),
        (3, StepType.DECISION, "Decision: Remove content automatically",
         {"confidence": 0.89, "source": "hybrid", "violation_type": "spam"}),
        (4, StepType.ACTION, "Removing content and sending notification to user",
         {"notification_sent": True, "appeal_available": True}),
        (5, StepType.OUTCOME, "Content removed. User can appeal within 7 days.",
         {"appeal_deadline": "2026-01-27", "strike_count": 1})
    ]
    
    for order, step_type, content, metadata in steps:
        step = DecisionStep(
            decision_id=decision.id,
            step_order=order,
            step_type=step_type,
            content=content,
            metadata=metadata,
            timestamp=base_time + timedelta(milliseconds=order * 500)
        )
        db.add(step)
    
    db.commit()
    
    print(f"[FLAGGED] Created: Content moderation ({decision.decision_id})")


def create_loan_approval(db, minutes_ago=0):
    """Loan approval using hybrid decision"""
    base_time = datetime.utcnow() - timedelta(minutes=minutes_ago)
    
    decision = Decision(
        decision_id=f"dec_{uuid.uuid4().hex[:12]}",
        timestamp=base_time,
        input_data={
            "request_type": "personal_loan",
            "amount": 15000.00,
            "term_months": 36,
            "applicant_id": "app_33221"
        },
        system_state={
            "credit_score": 720,
            "income_annual": 65000.00,
            "debt_to_income": 0.28,
            "employment_years": 4
        },
        reasoning="Credit score (720) exceeds minimum threshold (680). Debt-to-income ratio (28%) is healthy. Stable employment (4 years). LLM analysis of application documents shows consistent income history. Risk assessment: Low.",
        decision="approve_loan",
        confidence=0.91,
        source=DecisionSource.HYBRID,
        outcome="Loan approved with interest rate 6.5%",
        outcome_data={
            "interest_rate": 0.065,
            "monthly_payment": 458.72,
            "total_repayment": 16514.00
        },
        tags=["loan", "approved", "personal_loan"]
    )
    
    db.add(decision)
    db.flush()
    
    steps = [
        (0, StepType.INPUT, "Loan application received: $15,000 for 36 months",
         {"application_id": "LN-2026-00892"}),
        (1, StepType.REASONING, "Performing credit check and income verification...",
         {"credit_bureau": "Experian", "income_verified": True}),
        (2, StepType.REASONING, "Credit score: 720 (Good). DTI: 28% (Healthy). Employment: Stable (4 years).",
         {"credit_tier": "good", "risk_category": "low"}),
        (3, StepType.REASONING, "LLM analyzing supporting documents (pay stubs, tax returns)...",
         {"model": "gpt-4", "documents_analyzed": 5}),
        (4, StepType.REASONING, "Document analysis: Income consistent, no red flags detected.",
         {"anomaly_score": 0.05, "fraud_risk": "very_low"}),
        (5, StepType.DECISION, "Decision: Approve loan at standard rate (6.5% APR)",
         {"confidence": 0.91, "source": "hybrid", "rate_tier": "standard"}),
        (6, StepType.ACTION, "Generating loan agreement and notification",
         {"agreement_id": "AGR-2026-00892"}),
        (7, StepType.OUTCOME, "Loan approved. Funds available in 2-3 business days.",
         {"disbursement_method": "direct_deposit", "estimated_date": "2026-01-23"})
    ]
    
    for order, step_type, content, metadata in steps:
        step = DecisionStep(
            decision_id=decision.id,
            step_order=order,
            step_type=step_type,
            content=content,
            metadata=metadata,
            timestamp=base_time + timedelta(seconds=order * 2)
        )
        db.add(step)
    
    db.commit()
    
    print(f"[LOAN APPROVED] Created: Loan approval ({decision.decision_id})")


if __name__ == "__main__":
    create_demo_decisions()
