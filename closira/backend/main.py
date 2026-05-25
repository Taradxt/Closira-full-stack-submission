from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta
import logging

from database import get_db, init_db, Enquiry, HistoryLog
from tasks import process_enquiry, log_event

init_db()

app = FastAPI(
    title="Closira API",
    description="AI-powered customer enquiry handling backend for SMBs. Handles WhatsApp, email, and call enquiries with async SOP matching.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

logger = logging.getLogger("closira")

# ── Schemas ──

class EnquiryCreate(BaseModel):
    customer_name: str
    channel: str        # whatsapp / email / call
    message: str

    class Config:
        json_schema_extra = {"example": {
            "customer_name": "Sarah M.",
            "channel": "whatsapp",
            "message": "Hi I want to book an appointment for tomorrow"
        }}

class FollowUpCreate(BaseModel):
    delay_minutes: int = 30
    message_template: Optional[str] = "Following up on your enquiry!"

    class Config:
        json_schema_extra = {"example": {
            "delay_minutes": 60,
            "message_template": "Just checking in on your enquiry!"
        }}

class EscalateCreate(BaseModel):
    reason: str

    class Config:
        json_schema_extra = {"example": {
            "reason": "Customer requested to speak to a manager"
        }}

# ── Endpoints ──

@app.get("/health", tags=["Health"])
def health_check(db: Session = Depends(get_db)):
    """Returns API status and database connectivity."""
    try:
        import sqlalchemy
        db.execute(sqlalchemy.text("SELECT 1"))
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
    return {
        "status": "ok",
        "database": db_status,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/enquiry", status_code=202, tags=["Enquiries"])
def create_enquiry(
    payload: EnquiryCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Create a new inbound customer enquiry.
    Returns a job ID immediately — SOP matching runs in background.
    """
    if payload.channel not in ["whatsapp", "email", "call"]:
        raise HTTPException(status_code=422, detail="channel must be: whatsapp, email, or call")

    enquiry = Enquiry(
        customer_name=payload.customer_name,
        channel=payload.channel,
        message=payload.message,
        status="new"
    )
    db.add(enquiry)
    db.add(HistoryLog(
        enquiry_id=enquiry.id,
        event="enquiry_created",
        detail=f"Channel: {payload.channel} | Customer: {payload.customer_name}"
    ))
    db.commit()

    log_event("enquiry_created", f"id={enquiry.id} channel={payload.channel}")
    background_tasks.add_task(process_enquiry, enquiry.id)

    return {
        "job_id": enquiry.id,
        "status": "accepted",
        "message": "Enquiry received. SOP matching running in background."
    }

@app.post("/enquiry/{enquiry_id}/followup", tags=["Enquiries"])
def schedule_followup(
    enquiry_id: str,
    payload: FollowUpCreate,
    db: Session = Depends(get_db)
):
    """Schedule a follow-up for an open enquiry."""
    enquiry = db.query(Enquiry).filter(Enquiry.id == enquiry_id).first()
    if not enquiry:
        raise HTTPException(status_code=404, detail="Enquiry not found")
    if enquiry.status == "escalated":
        raise HTTPException(status_code=400, detail="Cannot schedule follow-up on an escalated enquiry")

    due_at = datetime.utcnow() + timedelta(minutes=payload.delay_minutes)
    db.add(HistoryLog(
        enquiry_id=enquiry_id,
        event="followup_scheduled",
        detail=f"Due: {due_at.isoformat()} | Template: {payload.message_template}"
    ))
    db.commit()

    return {
        "enquiry_id": enquiry_id,
        "followup_due_at": due_at.isoformat(),
        "message_template": payload.message_template
    }

@app.post("/enquiry/{enquiry_id}/escalate", tags=["Enquiries"])
def escalate_enquiry(
    enquiry_id: str,
    payload: EscalateCreate,
    db: Session = Depends(get_db)
):
    """Mark an enquiry as escalated to a human agent."""
    enquiry = db.query(Enquiry).filter(Enquiry.id == enquiry_id).first()
    if not enquiry:
        raise HTTPException(status_code=404, detail="Enquiry not found")

    enquiry.status = "escalated"
    enquiry.escalation_reason = payload.reason
    db.add(HistoryLog(
        enquiry_id=enquiry_id,
        event="manually_escalated",
        detail=f"Reason: {payload.reason}"
    ))
    db.commit()
    log_event("escalation_triggered", f"id={enquiry_id} reason={payload.reason}")

    return {
        "enquiry_id": enquiry_id,
        "status": "escalated",
        "reason": payload.reason
    }

@app.get("/enquiry/{enquiry_id}/history", tags=["Enquiries"])
def get_history(enquiry_id: str, db: Session = Depends(get_db)):
    """Return full conversation history and status timeline for an enquiry."""
    enquiry = db.query(Enquiry).filter(Enquiry.id == enquiry_id).first()
    if not enquiry:
        raise HTTPException(status_code=404, detail="Enquiry not found")

    logs = db.query(HistoryLog)\
             .filter(HistoryLog.enquiry_id == enquiry_id)\
             .order_by(HistoryLog.timestamp).all()

    return {
        "enquiry": {
            "id": enquiry.id,
            "customer_name": enquiry.customer_name,
            "channel": enquiry.channel,
            "message": enquiry.message,
            "status": enquiry.status,
            "sop_matched": enquiry.sop_matched,
            "suggested_response": enquiry.suggested_response,
            "escalation_reason": enquiry.escalation_reason,
            "created_at": enquiry.created_at.isoformat()
        },
        "timeline": [
            {
                "event": log.event,
                "detail": log.detail,
                "timestamp": log.timestamp.isoformat()
            }
            for log in logs
        ]
    }
