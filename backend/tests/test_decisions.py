"""
Unit tests for decision API endpoints
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine

client = TestClient(app)

# Create test database
Base.metadata.create_all(bind=engine)


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_create_decision():
    """Test creating a new decision"""
    decision_data = {
        "input_data": {"user_id": "test_user", "request": "test_request"},
        "system_state": {"test": "state"},
        "reasoning": "This is a test decision",
        "decision": "test_approve",
        "confidence": 0.95,
        "source": "rule",
        "tags": ["test"]
    }
    
    response = client.post("/api/decisions", json=decision_data)
    assert response.status_code == 201
    
    data = response.json()
    assert "decision_id" in data
    assert data["decision"] == "test_approve"
    assert data["confidence"] == 0.95


def test_get_decisions():
    """Test retrieving decisions list"""
    response = client.get("/api/decisions")
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, list)


def test_get_decision_by_id():
    """Test retrieving a specific decision"""
    # First create a decision
    decision_data = {
        "input_data": {"test": "data"},
        "reasoning": "Test reasoning",
        "decision": "test_decision",
        "confidence": 0.85,
        "source": "llm"
    }
    
    create_response = client.post("/api/decisions", json=decision_data)
    decision_id = create_response.json()["decision_id"]
    
    # Then retrieve it
    response = client.get(f"/api/decisions/{decision_id}")
    assert response.status_code == 200
    
    data = response.json()
    assert data["decision_id"] == decision_id
    assert data["decision"] == "test_decision"


def test_get_decision_replay():
    """Test replay endpoint"""
    # Create a decision
    decision_data = {
        "input_data": {"test": "data"},
        "reasoning": "Test reasoning",
        "decision": "test_decision",
        "confidence": 0.9,
        "source": "hybrid"
    }
    
    create_response = client.post("/api/decisions", json=decision_data)
    decision_id = create_response.json()["decision_id"]
    
    # Get replay data
    response = client.get(f"/api/decisions/{decision_id}/replay")
    assert response.status_code == 200
    
    data = response.json()
    assert "decision" in data
    assert "total_steps" in data
    assert data["total_steps"] > 0


def test_get_stats():
    """Test statistics endpoint"""
    response = client.get("/api/traces/stats")
    assert response.status_code == 200
    
    data = response.json()
    assert "total_decisions" in data
    assert "average_confidence" in data
    assert "decisions_by_source" in data


def test_filter_by_source():
    """Test filtering decisions by source"""
    response = client.get("/api/decisions?source=rule")
    assert response.status_code == 200


def test_filter_by_confidence():
    """Test filtering decisions by confidence"""
    response = client.get("/api/decisions?min_confidence=0.8")
    assert response.status_code == 200


def test_invalid_decision():
    """Test creating decision with invalid data"""
    invalid_data = {
        "input_data": {},
        "decision": "test",
        "confidence": 1.5,  # Invalid - must be 0-1
        "source": "rule"
    }
    
    response = client.post("/api/decisions", json=invalid_data)
    assert response.status_code == 422  # Validation error
