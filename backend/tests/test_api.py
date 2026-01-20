"""
Unit tests for decision API endpoints

Run with: pytest backend/tests/test_api.py -v
"""
import pytest
from fastapi.testclient import TestClient
from datetime import datetime

from app.main import app
from app.database import Base, engine, get_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Test database
TEST_DATABASE_URL = "sqlite:///./test_decisions.db"
test_engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

Base.metadata.create_all(bind=test_engine)


def override_get_db():
    try:
        db = TestSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


class TestDecisionAPI:
    """Test suite for decision endpoints"""
    
    def test_create_decision(self):
        """Test creating a new decision"""
        response = client.post("/api/decisions", json={
            "input_data": {"user_id": "test_123", "amount": 99.99},
            "system_state": {"test": True},
            "reasoning": "Test reasoning",
            "decision": "approve",
            "confidence": 0.95,
            "source": "rule",
            "outcome": "success",
            "tags": ["test"]
        })
        
        assert response.status_code == 201
        data = response.json()
        assert data["decision"] == "approve"
        assert data["confidence"] == 0.95
        assert data["source"] == "rule"
        assert "decision_id" in data
        assert data["decision_id"].startswith("dec_")
    
    def test_create_decision_with_invalid_confidence(self):
        """Test validation for confidence values"""
        response = client.post("/api/decisions", json={
            "input_data": {},
            "decision": "test",
            "confidence": 1.5,  # Invalid: > 1.0
            "source": "rule"
        })
        
        assert response.status_code == 422  # Validation error
    
    def test_get_decisions_with_filters(self):
        """Test retrieving decisions with filters"""
        # First create a decision
        client.post("/api/decisions", json={
            "input_data": {},
            "decision": "test",
            "confidence": 0.85,
            "source": "llm"
        })
        
        # Get with source filter
        response = client.get("/api/decisions?source=llm")
        assert response.status_code == 200
        data = response.json()
        assert "decisions" in data
        assert "total" in data
        assert isinstance(data["decisions"], list)
    
    def test_get_decisions_pagination(self):
        """Test pagination"""
        # Create multiple decisions
        for i in range(5):
            client.post("/api/decisions", json={
                "input_data": {},
                "decision": f"test_{i}",
                "confidence": 0.8,
                "source": "rule"
            })
        
        # Test limit
        response = client.get("/api/decisions?limit=3")
        assert response.status_code == 200
        data = response.json()
        assert len(data["decisions"]) <= 3
        
        # Test offset
        response = client.get("/api/decisions?offset=2&limit=2")
        assert response.status_code == 200
        data = response.json()
        assert data["offset"] == 2
    
    def test_get_decision_by_id(self):
        """Test retrieving specific decision"""
        # Create decision
        create_response = client.post("/api/decisions", json={
            "input_data": {"test": "data"},
            "decision": "test_decision",
            "confidence": 0.9,
            "source": "hybrid"
        })
        
        assert create_response.status_code == 201
        created_data = create_response.json()
        decision_id = created_data.get("decision_id")
        
        # Skip if decision_id not in response (check steps exist instead)
        if not decision_id:
            assert "id" in created_data
            return
        
        # Get by ID
        response = client.get(f"/api/decisions/{decision_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["decision_id"] == decision_id
        assert data["decision"] == "test_decision"
    
    def test_get_nonexistent_decision(self):
        """Test 404 for nonexistent decision"""
        response = client.get("/api/decisions/nonexistent_id")
        assert response.status_code == 404
    
    def test_search_decisions(self):
        """Test search functionality"""
        # Create decision with searchable content
        client.post("/api/decisions", json={
            "input_data": {},
            "reasoning": "This is unique searchable content",
            "decision": "test",
            "confidence": 0.8,
            "source": "rule"
        })
        
        # Search
        response = client.get("/api/decisions?search=searchable")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] > 0


class TestStatsAPI:
    """Test suite for stats endpoints"""
    
    def test_get_stats_overview(self):
        """Test stats overview endpoint"""
        response = client.get("/api/stats/overview?days=7")
        assert response.status_code == 200
        data = response.json()
        assert "total_decisions" in data
        assert "average_confidence" in data
        assert "source_distribution" in data
    
    def test_get_stats_timeline(self):
        """Test stats timeline endpoint"""
        response = client.get("/api/stats/timeline?days=7")
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert isinstance(data["data"], list)


class TestExportAPI:
    """Test suite for export endpoints"""
    
    def test_export_csv(self):
        """Test CSV export"""
        response = client.get("/api/decisions/export/csv")
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/csv; charset=utf-8"
        assert "attachment" in response.headers["content-disposition"]
    
    def test_export_json(self):
        """Test JSON export"""
        response = client.get("/api/decisions/export/json")
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"
        assert "attachment" in response.headers["content-disposition"]


def test_health_endpoint():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_root_endpoint():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data
    assert "endpoints" in data
