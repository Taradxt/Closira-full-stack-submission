from sqlalchemy import create_engine, Column, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import uuid

DATABASE_URL = "sqlite:///./closira.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

class Enquiry(Base):
    __tablename__ = "enquiries"
    id                 = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    customer_name      = Column(String, nullable=False)
    channel            = Column(String, nullable=False)
    message            = Column(Text, nullable=False)
    status             = Column(String, default="new")
    sop_matched        = Column(String, nullable=True)
    suggested_response = Column(Text, nullable=True)
    escalation_reason  = Column(String, nullable=True)
    created_at         = Column(DateTime, default=datetime.utcnow)
    updated_at         = Column(DateTime, default=datetime.utcnow)

class HistoryLog(Base):
    __tablename__ = "history_logs"
    id         = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    enquiry_id = Column(String, nullable=False)
    event      = Column(String, nullable=False)
    detail     = Column(Text, nullable=True)
    timestamp  = Column(DateTime, default=datetime.utcnow)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    Base.metadata.create_all(bind=engine)
