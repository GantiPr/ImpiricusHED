from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, ConfigDict
import logging
import json
from dateutil import parser

from app.database import get_db, Physician, Message

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Schemas
class PhysicianResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    physician_id: int
    npi: str
    first_name: str
    last_name: str
    specialty: str
    state: str
    consent_opt_in: bool
    preferred_channel: str


class MessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    message_id: int
    physician_id: int
    physician_name: Optional[str] = None
    specialty: Optional[str] = None
    state: Optional[str] = None
    channel: str
    direction: str
    timestamp: datetime
    message_text: str
    campaign_id: str
    topic: str
    compliance_tag: str
    sentiment: str
    delivery_status: str
    response_latency_sec: Optional[float]


class ComplianceResult(BaseModel):
    message_id: int
    message_text: str
    matched_rules: List[dict]
    action_required: Optional[str]
    modified_text: Optional[str]


# Compliance Checker
class ComplianceChecker:
    def __init__(self, policies_path: str = "data/compliance_policies.json"):
        import os
        # Handle both root and backend directory execution
        if not os.path.exists(policies_path):
            policies_path = f"../{policies_path}"
        with open(policies_path, 'r') as f:
            self.policies = json.load(f)
        self.rules = self.policies.get("rules", [])
    
    def check_message(self, message_text: str) -> dict:
        """Check message against compliance rules"""
        matched_rules = []
        actions = []
        modified_text = message_text
        
        for rule in self.rules:
            keywords = rule.get("keywords_any", [])
            
            # Check if any keyword matches
            if any(keyword.lower() in message_text.lower() for keyword in keywords):
                matched_rules.append({
                    "rule_id": rule["id"],
                    "rule_name": rule["name"]
                })
                
                # Handle action
                if "action" in rule:
                    actions.append(rule["action"])
                
                # Handle required append
                if "requires_append" in rule:
                    append_text = rule["requires_append"]
                    if append_text not in modified_text:
                        modified_text = f"{modified_text} {append_text}"
        
        # Determine primary action
        action_required = None
        if "reject" in actions:
            action_required = "reject"
        elif "flag" in actions:
            action_required = "flag"
        elif "route_to_rep" in actions:
            action_required = "route_to_rep"
        
        return {
            "matched_rules": matched_rules,
            "action_required": action_required,
            "modified_text": modified_text if modified_text != message_text else None
        }


# FastAPI App
app = FastAPI(title="Healthcare Engagement Dashboard API")
compliance_checker = ComplianceChecker()

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://frontend:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Simple request logging
@app.middleware("http")
async def log_requests(request, call_next):
    response = await call_next(request)
    logger.info(f"{request.method} {request.url.path} - {response.status_code}")
    return response


@app.get("/")
def root():
    return {"message": "Healthcare Engagement Dashboard API", "version": "1.0"}


@app.get("/physicians", response_model=List[PhysicianResponse])
def get_physicians(
    state: Optional[str] = None,
    specialty: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Physician)
    
    if state:
        query = query.filter(Physician.state == state.upper())
    if specialty:
        query = query.filter(Physician.specialty == specialty)
    
    return query.all()


@app.get("/messages/date-range")
def get_date_range(db: Session = Depends(get_db)):
    result = db.query(
        func.min(Message.timestamp).label('min_date'),
        func.max(Message.timestamp).label('max_date')
    ).first()
    
    return {
        "min_date": result.min_date.date().isoformat() if result.min_date else None,
        "max_date": result.max_date.date().isoformat() if result.max_date else None
    }


@app.get("/messages", response_model=List[MessageResponse])
def get_messages(
    physician_id: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    topic: Optional[str] = None,
    sentiment: Optional[str] = None,
    message_text: Optional[str] = None,
    specialty: Optional[str] = None,
    state: Optional[str] = None,
    db: Session = Depends(get_db)
):
    # Join messages with physicians
    query = db.query(
        Message,
        Physician.first_name,
        Physician.last_name,
        Physician.specialty,
        Physician.state
    ).join(Physician, Message.physician_id == Physician.physician_id)
    
    if physician_id:
        query = query.filter(Message.physician_id == physician_id)
    
    if start_date:
        try:
            start_dt = parser.parse(start_date)
            query = query.filter(Message.timestamp >= start_dt)
        except:
            raise HTTPException(status_code=400, detail="Invalid date format")
    
    if end_date:
        try:
            end_dt = parser.parse(end_date)
            query = query.filter(Message.timestamp <= end_dt)
        except:
            raise HTTPException(status_code=400, detail="Invalid date format")
    
    if topic:
        query = query.filter(Message.topic == topic)
    
    if sentiment:
        query = query.filter(Message.sentiment == sentiment)
    
    if message_text:
        query = query.filter(Message.message_text.like(f'%{message_text}%'))
    
    if specialty:
        query = query.filter(Physician.specialty == specialty)
    
    if state:
        query = query.filter(Physician.state == state.upper())
    
    results = query.order_by(Message.timestamp.desc()).all()
    
    # Format results with physician data
    messages = []
    for msg, first_name, last_name, specialty, state in results:
        message_dict = {
            "message_id": msg.message_id,
            "physician_id": msg.physician_id,
            "physician_name": f"{first_name} {last_name}",
            "specialty": specialty,
            "state": state,
            "channel": msg.channel,
            "direction": msg.direction,
            "timestamp": msg.timestamp,
            "message_text": msg.message_text,
            "campaign_id": msg.campaign_id,
            "topic": msg.topic,
            "compliance_tag": msg.compliance_tag,
            "sentiment": msg.sentiment,
            "delivery_status": msg.delivery_status,
            "response_latency_sec": msg.response_latency_sec
        }
        messages.append(MessageResponse(**message_dict))
    
    return messages


@app.post("/classify/{message_id}", response_model=ComplianceResult)
def classify_message(message_id: int, db: Session = Depends(get_db)):
    message = db.query(Message).filter(Message.message_id == message_id).first()
    
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    result = compliance_checker.check_message(message.message_text)
    
    return ComplianceResult(
        message_id=message_id,
        message_text=message.message_text,
        matched_rules=result["matched_rules"],
        action_required=result["action_required"],
        modified_text=result["modified_text"]
    )
