import logging, json
from datetime import datetime
from database import SessionLocal, Enquiry, HistoryLog

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("closira")

# 5 hardcoded SOPs -- keyword matching, no AI required
SOPS = {
    "booking_enquiry": {
        "keywords": ["book", "appointment", "schedule", "reserve", "slot"],
        "response": "Thank you for your booking enquiry! We will confirm your appointment within 2 hours."
    },
    "pricing_question": {
        "keywords": ["price", "cost", "rate", "charge", "fee", "how much"],
        "response": "Our pricing starts from Rs.999. Reply for a custom quote."
    },
    "complaint": {
        "keywords": ["complaint", "unhappy", "problem", "issue", "bad", "wrong", "disappointed"],
        "response": "We are sorry to hear this. A manager will contact you within 1 hour."
    },
    "after_hours": {
        "keywords": ["tonight", "weekend", "sunday", "saturday", "closed", "after hours"],
        "response": "We are currently offline. We will respond by 9am tomorrow."
    },
    "general_info": {
        "keywords": ["info", "information", "details", "tell me", "what is", "how does"],
        "response": "Thanks for your interest! Here are our service details..."
    }
}

def match_sop(message: str):
    msg = message.lower()
    for name, sop in SOPS.items():
        for kw in sop["keywords"]:
            if kw in msg:
                return name, sop["response"]
    return None, None

def log_event(event: str, detail: str = ""):
    logger.info(json.dumps({
        "timestamp": datetime.utcnow().isoformat(),
        "event": event,
        "detail": detail
    }))

def process_enquiry(enquiry_id: str):
    db = SessionLocal()
    try:
        enquiry = db.query(Enquiry).filter(Enquiry.id == enquiry_id).first()
        if not enquiry:
            return
        log_event("task_processing_started", f"enquiry_id={enquiry_id}")
        sop_name, response = match_sop(enquiry.message)
        if sop_name:
            enquiry.status             = "matched"
            enquiry.sop_matched        = sop_name
            enquiry.suggested_response = response
            log_event("sop_matched", f"id={enquiry_id} sop={sop_name}")
            db.add(HistoryLog(enquiry_id=enquiry_id, event="sop_matched", detail=f"Matched: {sop_name}"))
        else:
            enquiry.status            = "escalated"
            enquiry.escalation_reason = "No SOP matched for this message"
            log_event("escalation_triggered", f"id={enquiry_id} reason=no_sop_match")
            db.add(HistoryLog(enquiry_id=enquiry_id, event="auto_escalated", detail="No SOP matched — escalated"))
        db.commit()
        log_event("task_completed", f"enquiry_id={enquiry_id}")
    except Exception as e:
        log_event("task_error", str(e))
    finally:
        db.close()
