# Closira — Full Stack Submission

Built by **Tarika Dixit** | tarikadixit2002@gmail.com | 9667556234

---

## Project Structure

```
closira/
├── backend/         ← FastAPI + SQLite REST API
│   ├── main.py
│   ├── database.py
│   ├── tasks.py
│   ├── requirements.txt
│   └── README.md
│
├── frontend/        ← Mobile dashboard (HTML/CSS/JS)
│   ├── index.html
│   └── README.md
│
└── README.md        ← this file
```

---

## Backend — Quick Start

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

API docs: http://localhost:8000/docs

---

## Frontend — Quick Start

```bash
cd frontend
open index.html
# or
npx serve .
```

---

## Key Decisions

**SQLite over PostgreSQL** — zero setup for a prototype. Swap DATABASE_URL for production.

**FastAPI BackgroundTasks over Celery** — no broker needed, built-in, sufficient for this scale.

**Web app over React Native** — delivers all 5 required screens fully functional in the given time. Same component thinking, same UX logic.

**5 hardcoded SOPs** — keyword matching as specified. Production would use NLP/LLM.

## Trade-offs Acknowledged

- SOP matching is naive keyword search — not ML
- No auth, no multi-tenancy (stubbed in schema design)
- Frontend is web, not native — all screens and navigation work correctly
- No actual notification sending for follow-ups — logged only
