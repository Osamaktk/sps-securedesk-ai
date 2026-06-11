# SPS SecureDesk AI

SPS SecureDesk AI is an AI-assisted enterprise helpdesk platform designed to replace a legacy osTicket workflow with a unified ticketing system. The platform receives support requests from multiple channels, stores them in one ticket model, and gives support staff a consistent workflow for triage, approval, SLA tracking, audit logging, and resolution.

> Current repository status: Dev 1 backend/ticket engine scaffold is implemented. Email worker, AI layer, and frontend portal are planned integration modules owned by separate developers.

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Environment Variables](#environment-variables)
- [Running the API](#running-the-api)
- [API Overview](#api-overview)
- [Integration Notes for Other Developers](#integration-notes-for-other-developers)
- [Development Workflow](#development-workflow)
- [Security Notes](#security-notes)
- [Roadmap](#roadmap)

## Features

- Unified ticket model for `email`, `portal_form`, and `chat` sources
- User registration and JWT-based authentication
- Role-based access control for requesters, agents, managers, and security admins
- Ticket create, list, detail, and update endpoints
- Timeline events for ticket history and agent activity
- High-risk ticket approval workflow
- SLA due-date calculation based on priority
- File attachment upload with size and type validation
- Immutable audit logging with channel tracking
- Management summary reporting endpoint
- Alembic migration setup for database schema management
- Dockerfile for backend containerization

## Tech Stack

| Area | Technology |
| --- | --- |
| API Framework | FastAPI |
| Language | Python 3.11 |
| Database ORM | SQLAlchemy 2.x async |
| Migrations | Alembic |
| Validation | Pydantic v2 |
| Auth | JWT via `python-jose`, password hashing via `passlib` |
| Databases | PostgreSQL for production, SQLite supported for local development |
| Server | Uvicorn |

## Project Structure

```text
sps-securedesk-ai/
+-- backend/
|   +-- alembic/              # Database migrations
|   +-- middleware/           # Auth and role dependencies
|   +-- models/               # SQLAlchemy database models
|   +-- routes/               # FastAPI route modules
|   +-- schemas/              # Pydantic request/response schemas
|   +-- services/             # Business logic
|   +-- .env.example          # Backend environment template
|   +-- Dockerfile            # Backend container definition
|   +-- alembic.ini           # Alembic configuration
|   +-- database.py           # Database engine/session setup
|   +-- main.py               # FastAPI application entry point
|   +-- requirements.txt      # Python dependencies
+-- README.md
```

## Getting Started

### Prerequisites

- Python 3.11+
- Git
- PostgreSQL if you want to test with a production-like database
- Optional: Docker for containerized backend runs

### Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/sps-securedesk-ai.git
cd sps-securedesk-ai
```

### Create a Virtual Environment

PowerShell:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Bash:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Configure Environment

Copy the backend environment template:

```bash
cp .env.example .env
```

For quick local development, you can use SQLite by setting:

```env
DATABASE_URL=sqlite+aiosqlite:///./securedesk.db
DATABASE_URL_SYNC=sqlite:///./securedesk.db
SECRET_KEY=replace-with-a-local-development-secret
ENVIRONMENT=development
```

With SQLite and `ENVIRONMENT=development`, the backend creates tables automatically on startup.

For PostgreSQL, configure `DATABASE_URL` and `DATABASE_URL_SYNC`, then run Alembic migrations:

```bash
alembic upgrade head
```

## Environment Variables

The backend reads environment variables from `backend/.env`.

| Variable | Required | Description |
| --- | --- | --- |
| `DATABASE_URL` | Yes | Async SQLAlchemy database URL |
| `DATABASE_URL_SYNC` | Yes for Alembic | Sync database URL used by migrations |
| `SECRET_KEY` | Yes | JWT signing secret |
| `ALGORITHM` | No | JWT algorithm, defaults to `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No | Token lifetime in minutes |
| `UPLOAD_DIR` | No | Attachment storage folder |
| `MAX_UPLOAD_SIZE_MB` | No | Attachment upload size limit |
| `ENVIRONMENT` | No | Use `development` locally |
| `CORS_ORIGINS` | No | Comma-separated frontend origins |

Never commit real `.env` files or production secrets.

## Running the API

From the `backend/` directory:

```bash
uvicorn main:app --reload
```

Default local URLs:

- API root/docs: `http://127.0.0.1:8000/docs`
- OpenAPI JSON: `http://127.0.0.1:8000/openapi.json`
- Health check: `http://127.0.0.1:8000/health`

Expected health response:

```json
{
  "status": "ok",
  "service": "SPS SecureDesk AI"
}
```

## API Overview

### Auth

| Method | Endpoint | Description |
| --- | --- | --- |
| `POST` | `/auth/register` | Register a user |
| `POST` | `/auth/login` | Login and receive a JWT token |

### Tickets

| Method | Endpoint | Description | Auth |
| --- | --- | --- | --- |
| `POST` | `/tickets` | Create a ticket | Optional |
| `GET` | `/tickets` | List tickets visible to the user | Required |
| `GET` | `/tickets/{ticket_id}` | Get one ticket with timeline and attachments | Required |
| `PATCH` | `/tickets/{ticket_id}` | Update ticket fields | Agent+ |

### Timeline, Attachments, Approvals, Reports

| Method | Endpoint | Description | Auth |
| --- | --- | --- | --- |
| `POST` | `/tickets/{ticket_id}/events` | Add a timeline event | Agent+ |
| `POST` | `/tickets/{ticket_id}/attachments` | Upload an attachment | Required |
| `POST` | `/tickets/{ticket_id}/approve` | Approve or reject high-risk ticket | Security Admin / Manager / Admin |
| `GET` | `/reports/summary` | Management report summary | Manager / Admin |

## Example Requests

### Register a User

```bash
curl -X POST http://127.0.0.1:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "agent@example.com",
    "full_name": "SPS Agent",
    "password": "StrongPassword123",
    "role": "agent"
  }'
```

### Login

```bash
curl -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "agent@example.com",
    "password": "StrongPassword123"
  }'
```

### Create a Ticket

```bash
curl -X POST http://127.0.0.1:8000/tickets \
  -H "Content-Type: application/json" \
  -d '{
    "source": "portal_form",
    "subject": "Cannot access VPN",
    "description": "VPN login fails after password reset.",
    "category": "identity_access",
    "priority": "medium",
    "requester_email": "requester@example.com"
  }'
```

Allowed ticket sources:

- `email`
- `portal_form`
- `chat`

## Integration Notes for Other Developers

All intake channels must create tickets through the same backend endpoint:

```text
POST /tickets
```

Expected source ownership:

| Developer | Module | Ticket Source |
| --- | --- | --- |
| Dev 2 | Email pipeline | `email` |
| Dev 3 | AI chat escalation | `chat` |
| Dev 4 | Frontend submit request form | `portal_form` |

Other modules should consume the backend API instead of editing `backend/` directly.

## Development Workflow

Recommended branch structure:

```text
main                         # Stable final branch
dev                          # Integration branch
feature/ticket-engine        # Dev 1 backend work
feature/email-pipeline       # Dev 2 email work
feature/ai-chat              # Dev 3 AI work
feature/frontend-portal      # Dev 4 frontend work
```

Daily workflow:

```bash
git checkout feature/ticket-engine
git pull origin dev
```

Before opening a pull request:

```bash
python -m compileall -q backend
git status
```

Pull requests should target `dev`, not `main`.

## Security Notes

- Do not commit `.env` files or real credentials.
- Use strong `SECRET_KEY` values outside local development.
- Keep requester, agent, and admin workflows role-protected.
- Validate all file uploads before storage.
- Use parameterized ORM queries through SQLAlchemy.
- Review CORS origins before deployment.

## Roadmap

- Email worker integration for IMAP/SMTP ticket intake
- AI chat assistant and ticket escalation bridge
- AI ticket classifier and summarizer
- React frontend portal and agent queue
- Docker Compose for full-stack local development
- End-to-end walkthrough scenarios across email, chat, and portal form
- Deployment to hosted backend/frontend environments
