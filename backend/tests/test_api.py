import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

from app.main import app
from app.database import Base, get_db, Physician, Message

# Test database
TEST_DATABASE_URL = "sqlite:///../data/test.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(scope="function")
def setup_database():
    """Create tables and add test data"""
    Base.metadata.create_all(bind=engine)
    
    db = TestingSessionLocal()
    
    # Add test physician
    physician = Physician(
        physician_id=101,
        npi="1089250953",
        first_name="Drew",
        last_name="Nguyen",
        specialty="Cardiology",
        state="MA",
        consent_opt_in=True,
        preferred_channel="sms"
    )
    db.add(physician)
    
    # Add test message
    message = Message(
        message_id=10001,
        physician_id=101,
        channel="sms",
        direction="outbound",
        timestamp=datetime(2025, 7, 25, 7, 14, 32),
        message_text="Clarify dosing schedule and titration.",
        campaign_id="CMP-01",
        topic="dosing",
        compliance_tag="needs_review",
        sentiment="neutral",
        delivery_status="delivered",
        response_latency_sec=None
    )
    db.add(message)
    
    db.commit()
    db.close()
    
    yield
    
    # Cleanup
    Base.metadata.drop_all(bind=engine)


def test_root():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


def test_get_physicians(setup_database):
    """Test GET /physicians endpoint"""
    response = client.get("/physicians")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["physician_id"] == 101
    assert data[0]["specialty"] == "Cardiology"


def test_get_physicians_filter_by_state(setup_database):
    """Test GET /physicians with state filter"""
    response = client.get("/physicians?state=MA")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["state"] == "MA"


def test_get_physicians_filter_by_specialty(setup_database):
    """Test GET /physicians with specialty filter"""
    response = client.get("/physicians?specialty=Cardiology")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["specialty"] == "Cardiology"


def test_get_messages(setup_database):
    """Test GET /messages endpoint"""
    response = client.get("/messages")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["message_id"] == 10001


def test_get_messages_filter_by_physician(setup_database):
    """Test GET /messages with physician_id filter"""
    response = client.get("/messages?physician_id=101")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["physician_id"] == 101


def test_get_messages_filter_by_date(setup_database):
    """Test GET /messages with date range filter"""
    response = client.get("/messages?start_date=2025-07-01&end_date=2025-07-31")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1


def test_classify_message(setup_database):
    """Test POST /classify/{message_id} endpoint"""
    response = client.post("/classify/10001")
    assert response.status_code == 200
    data = response.json()
    assert data["message_id"] == 10001
    assert "matched_rules" in data
    # Should match dosing rule
    assert len(data["matched_rules"]) > 0
    assert data["modified_text"] is not None
    assert "See PI for full safety info" in data["modified_text"]


def test_classify_message_not_found(setup_database):
    """Test POST /classify/{message_id} with invalid ID"""
    response = client.post("/classify/99999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()
