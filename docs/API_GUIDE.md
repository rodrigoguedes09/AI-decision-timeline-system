# API Usage Guide

Complete guide to using the AI Decision Timeline API.

## Base URL

Development: `http://localhost:8000/api`

## Authentication

Currently no authentication required (add as needed for production).

---

## Endpoints

### 1. Create Decision

Create a new decision record with automatic step generation.

**Endpoint**: `POST /api/decisions`

**Request Body**:
```json
{
  "input_data": {
    "user_id": "user_123",
    "request_type": "refund",
    "amount": 49.99
  },
  "system_state": {
    "user_tier": "premium",
    "account_age_days": 365
  },
  "reasoning": "User is premium tier with good history",
  "decision": "approve_refund",
  "confidence": 0.92,
  "source": "rule",
  "outcome": "Refund processed",
  "tags": ["refund", "auto_approved"]
}
```

**Response** (201 Created):
```json
{
  "id": 1,
  "decision_id": "dec_abc123def456",
  "timestamp": "2026-01-20T10:30:00Z",
  "input_data": {...},
  "system_state": {...},
  "reasoning": "User is premium tier with good history",
  "decision": "approve_refund",
  "confidence": 0.92,
  "source": "rule",
  "outcome": "Refund processed",
  "tags": ["refund", "auto_approved"],
  "steps": [
    {
      "id": 1,
      "step_order": 0,
      "step_type": "input",
      "content": "Input received: ...",
      "metadata": {},
      "timestamp": "2026-01-20T10:30:00Z"
    },
    ...
  ]
}
```

**Python Example**:
```python
import requests

response = requests.post(
    "http://localhost:8000/api/decisions",
    json={
        "input_data": {"user_query": "Need help"},
        "reasoning": "Query requires support",
        "decision": "route_to_support",
        "confidence": 0.88,
        "source": "hybrid"
    }
)

decision = response.json()
print(f"Created: {decision['decision_id']}")
```

---

### 2. Get Decisions (Timeline)

Retrieve list of decisions with filtering and pagination.

**Endpoint**: `GET /api/decisions`

**Query Parameters**:
- `limit` (int, default: 50, max: 500) - Number of results
- `offset` (int, default: 0) - Pagination offset
- `source` (enum) - Filter by source: `rule`, `llm`, `hybrid`, `manual`
- `min_confidence` (float, 0-1) - Minimum confidence score
- `tag` (string) - Filter by tag
- `sort` (enum, default: `desc`) - Sort order: `asc` or `desc`

**Examples**:

Get recent decisions:
```bash
GET /api/decisions?limit=20&sort=desc
```

Get high-confidence rule-based decisions:
```bash
GET /api/decisions?source=rule&min_confidence=0.9
```

Get decisions with specific tag:
```bash
GET /api/decisions?tag=refund
```

**Response** (200 OK):
```json
[
  {
    "id": 1,
    "decision_id": "dec_abc123def456",
    "timestamp": "2026-01-20T10:30:00Z",
    "decision": "approve_refund",
    "confidence": 0.92,
    "source": "rule",
    "outcome": "Refund processed",
    "tags": ["refund"],
    "step_count": 5
  },
  ...
]
```

---

### 3. Get Single Decision

Get full details of a specific decision.

**Endpoint**: `GET /api/decisions/{decision_id}`

**Response** (200 OK):
```json
{
  "id": 1,
  "decision_id": "dec_abc123def456",
  "timestamp": "2026-01-20T10:30:00Z",
  "input_data": {...},
  "system_state": {...},
  "reasoning": "...",
  "decision": "approve_refund",
  "confidence": 0.92,
  "source": "rule",
  "outcome": "Refund processed",
  "steps": [...]
}
```

**Errors**:
- 404 Not Found - Decision doesn't exist

---

### 4. Replay Decision

Get decision data optimized for step-by-step replay.

**Endpoint**: `GET /api/decisions/{decision_id}/replay`

**Response** (200 OK):
```json
{
  "decision": {...full decision with steps...},
  "total_steps": 5,
  "duration_seconds": 12.5
}
```

**Use Case**: Frontend replay mode uses this to display decisions step-by-step.

---

### 5. Delete Decision

Delete a decision and all its steps.

**Endpoint**: `DELETE /api/decisions/{decision_id}`

**Response**: 204 No Content

---

### 6. Get Statistics

Get aggregate statistics about decisions.

**Endpoint**: `GET /api/traces/stats`

**Query Parameters**:
- `days` (int, default: 7, max: 365) - Time period

**Response** (200 OK):
```json
{
  "period_days": 7,
  "total_decisions": 42,
  "decisions_by_source": {
    "rule": 25,
    "llm": 10,
    "hybrid": 5,
    "manual": 2
  },
  "average_confidence": 0.8654,
  "low_confidence_count": 3,
  "low_confidence_percentage": 7.14
}
```

---

### 7. Get Timeline Data

Get decision counts over time for visualization.

**Endpoint**: `GET /api/traces/timeline`

**Query Parameters**:
- `days` (int, default: 7) - Time period

**Response** (200 OK):
```json
{
  "timeline": [
    {
      "date": "2026-01-20",
      "count": 15
    },
    {
      "date": "2026-01-19",
      "count": 12
    },
    ...
  ]
}
```

---

### 8. Search Decisions

Search decisions by content.

**Endpoint**: `GET /api/traces/search`

**Query Parameters**:
- `query` (string, required) - Search term
- `limit` (int, default: 20, max: 100) - Max results

**Response** (200 OK):
```json
{
  "query": "refund",
  "total_results": 8,
  "results": [
    {
      "decision_id": "dec_abc123",
      "timestamp": "2026-01-20T10:30:00Z",
      "decision": "approve_refund",
      "reasoning": "User meets refund criteria...",
      "confidence": 0.92,
      "source": "rule"
    },
    ...
  ]
}
```

---

### 9. Get All Tags

Get list of all tags used in decisions.

**Endpoint**: `GET /api/traces/tags`

**Response** (200 OK):
```json
{
  "tags": [
    "refund",
    "support",
    "escalated",
    "auto_approved",
    "manual_review"
  ],
  "total_unique_tags": 5
}
```

---

## Data Models

### DecisionSource Enum
- `rule` - Rule-based decision
- `llm` - LLM-generated decision
- `hybrid` - Combination of rules and LLM
- `manual` - Manual/human decision

### StepType Enum
- `input` - Input data received
- `reasoning` - Decision reasoning process
- `decision` - Final decision made
- `action` - Action taken
- `outcome` - Final result

---

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid request data"
}
```

### 404 Not Found
```json
{
  "detail": "Decision not found"
}
```

### 422 Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "confidence"],
      "msg": "ensure this value is less than or equal to 1.0",
      "type": "value_error.number.not_le"
    }
  ]
}
```

---

## Rate Limiting

Currently no rate limiting. Add as needed for production.

---

## Interactive Documentation

Visit http://localhost:8000/docs for interactive Swagger UI.

Visit http://localhost:8000/redoc for ReDoc documentation.

---

## Best Practices

1. **Always provide reasoning** - Makes decisions understandable
2. **Use appropriate confidence scores** - Be honest about uncertainty
3. **Tag decisions** - Makes filtering and analysis easier
4. **Include system state** - Provides full context
5. **Set outcomes when known** - Closes the decision loop

---

## Integration Patterns

### Pattern 1: Rule Engine Integration
```python
def make_decision(input_data):
    # Your rule engine logic
    decision = rule_engine.evaluate(input_data)
    
    # Log to timeline
    requests.post("/api/decisions", json={
        "input_data": input_data,
        "reasoning": decision.explanation,
        "decision": decision.action,
        "confidence": decision.confidence,
        "source": "rule"
    })
    
    return decision
```

### Pattern 2: LLM Integration
```python
def make_llm_decision(prompt):
    # Call LLM
    response = openai.ChatCompletion.create(...)
    
    # Log to timeline
    requests.post("/api/decisions", json={
        "input_data": {"prompt": prompt},
        "reasoning": response.reasoning,
        "decision": response.decision,
        "confidence": response.confidence,
        "source": "llm"
    })
    
    return response
```

### Pattern 3: Async Decision Logging
```python
from threading import Thread

def log_decision_async(decision_data):
    Thread(target=lambda: requests.post("/api/decisions", json=decision_data)).start()

# Use in your code
log_decision_async({...})
```

---

## Questions?

Check the [README](../README.md) or open an issue on GitHub.
