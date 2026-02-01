from sqlalchemy import create_engine, Column, Integer, String, Boolean, Float, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "sqlite:///./data/healthcare_engagement.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Physician(Base):
    __tablename__ = "physicians"
    
    physician_id = Column(Integer, primary_key=True, index=True)
    npi = Column(String, unique=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    specialty = Column(String, index=True)
    state = Column(String, index=True)
    consent_opt_in = Column(Boolean)
    preferred_channel = Column(String)


class Message(Base):
    __tablename__ = "messages"
    
    message_id = Column(Integer, primary_key=True, index=True)
    physician_id = Column(Integer, index=True)
    channel = Column(String)
    direction = Column(String)
    timestamp = Column(DateTime, index=True)
    message_text = Column(String)
    campaign_id = Column(String)
    topic = Column(String)
    compliance_tag = Column(String, index=True)
    sentiment = Column(String)
    delivery_status = Column(String)
    response_latency_sec = Column(Float, nullable=True)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    Base.metadata.create_all(bind=engine)
