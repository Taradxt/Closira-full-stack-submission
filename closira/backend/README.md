# Closira Backend

FastAPI backend for Closira's customer enquiry-handling pipeline.

## Setup & Run

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

Open http://localhost:8000/docs for full Swagger UI.

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /health | API + DB status |
| POST | /enquiry | Create new enquiry (returns job_id immediately) |
| POST | /enquiry/{id}/followup | Schedule a follow-up |
| POST | /enquiry/{id}/escalate | Escalate to human agent |
| GET | /enquiry/{id}/history | Full conversation history |

## Database

**SQLite** — chosen over PostgreSQL because:
- Zero setup — no separate server process needed
- Perfect for a prototype/internship submission
- Easily swappable to PostgreSQL in production by changing DATABASE_URL

## Async Processing

**FastAPI BackgroundTasks** — chosen over Celery because:
- No Redis/RabbitMQ broker needed — simpler setup
- Built into FastAPI — no extra dependencies
- Sufficient for this scale of prototype
- Celery makes sense at production scale with high concurrency

## SOP Matching Logic

5 hardcoded SOPs matched via keyword search:
1. booking_enquiry — book, appointment, schedule, slot
2. pricing_question — price, cost, rate, how much
3. complaint — problem, issue, unhappy, wrong
4. after_hours — weekend, sunday, saturday, closed
5. general_info — info, details, tell me, what is

If no SOP matches → enquiry auto-escalated.

## Trade-offs & Known Limitations

- SOP matching is keyword-based, not AI — production would use NLP/LLM
- No authentication — production needs JWT/OAuth
- SQLite not suitable for concurrent production load
- No retry logic for failed background tasks
- Follow-up scheduling is logged only — no actual notification sent

## Built by
Tarika Dixit | tarikadixit2002@gmail.com
