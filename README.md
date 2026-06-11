# SPS SecureDesk AI

SPS SecureDesk AI is an AI-assisted enterprise helpdesk platform for managing IT support requests from email, a web portal, and AI chat escalation in one unified ticket queue.

The project replaces a legacy osTicket-style workflow with a modern FastAPI backend, role-based access control, a single ticket lifecycle, approval gates for high-risk requests, SLA tracking, audit logs, and management reporting.

> Current status: Dev 1 backend/ticket engine is implemented. Email worker, AI service, and frontend portal are integration modules owned by separate teammates.

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Docker Compose](#docker-compose)
- [Environment Variables](#environment-variables)
- [API Overview](#api-overview)
- [Example Requests](#example-requests)
- [Integration Contracts](#integration-contracts)
- [Walkthrough Scenarios](#walkthrough-scenarios)
- [Development Workflow](#development-workflow)
- [Security Notes](#security-notes)
- [Deployment Plan](#deployment-plan)
- [Team](#team)

## Features

- Unified ticket creation for `email`, `portal_form`, and `chat`
- Sequential ticket numbers in `SPS-YYYY-NNN` format
- JWT authentication with six user roles
- Role-based access control for requester, agent, security admin, manager, and admin workflows
- Ticket create, list, detail, update, timeline, attachment, approval, and report endpoints
- Identity access requests automatically marked high risk and blocked for approval
- SLA due date calculation by priority
- Immutable audit logging with channel field
- Security logging for injection attempts, secret leakage, brute force, forbidden role access, and oversized uploads
- File upload validation with size and MIME checks
- PostgreSQL-ready schema with Alembic migrations
- FastAPI `/docs` OpenAPI documentation
- Docker Compose support for local backend, PostgreSQL, and Mailhog

## Architecture

```text
                         +----------------------+
                         |      Frontend        |
                         | React portal / agent |
                         +----------+-----------+
                                    |
                       portal_form  |  REST API
                                    v
+------------+       +--------------+--------------+       +----------------+
| Email User | ----> | Email Worker / Threading    | ----> |                |
+------------+       | IMAP + SMTP + Mailhog       |       |                |
                     +--------------+--------------+       |                |
                                    |                      |                |
                                    v                      |                |
+------------+       +--------------+--------------+       | FastAPI Backend|
| Chat User  | ----> | AI Service / KB / Escalate  | ----> | Ticket Engine  |
+------------+       +--------------+--------------+       |                |
                                                           |                |
                                                           +-------+--------+
                                                                   |
                                                                   v
                                                           +-------+--------+
                                                           | PostgreSQL DB  |
                                                           | tickets/events |
                                                           | audit/uploads  |
                                                           +----------------+
```

### Intake Pipelines

```text
Email:
User email -> IMAP poller -> thread resolver -> POST /tickets or POST /tickets/{id}/events

Web form:
Portal form -> POST /tickets -> confirmation UI -> ticket appears in queue

AI chat:
Chat question -> KB search -> escalation decision -> POST /tickets with source=chat
```

## Tech Stack

| Area | Technology |
| --- | --- |
| Backend API | FastAPI |
| Language | Python 3.11 |
| ORM | SQLAlchemy 2.x async |
| Database | PostgreSQL, SQLite for quick local development |
| Migrations | Alembic |
| Validation | Pydantic v2 |
| Auth | JWT with `python-jose`, password hashing with `passlib[bcrypt]` |
| File Uploads | FastAPI multipart uploads |
| Local Email Testing | Mailhog |
| Server | Uvicorn |
| Container | Docker |

## Project Structure

```text
sps-securedesk-ai/
+-- backend/
|   +-- alembic/              # Database migrations
|   +-- middleware/           # Auth and security middleware
|   +-- models/               # SQLAlchemy models
|   +-- routes/               # FastAPI routers
|   +-- schemas/              # Pydantic schemas
|   +-- services/             # Business logic
|   +-- .env.example          # Backend environment template
|   +-- Dockerfile            # Backend container
|   +-- alembic.ini           # Alembic config
|   +-- database.py           # Async DB setup
|   +-- main.py               # FastAPI app entry
|   +-- requirements.txt      # Python dependencies
+-- docker-compose.yml        # Local DB, Mailhog, backend, optional teammate services
+-- README.md
```

## Getting Started

### Prerequisites

- Python 3.11+
- Git
- PostgreSQL for production-like local testing
- Docker Desktop for Compose-based setup

### Clone

```bash
git clone https://github.com/YOUR_USERNAME/sps-securedesk-ai.git
cd sps-securedesk-ai
```

### Local Python Setup

PowerShell:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Bash:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

For fast SQLite development, set these values in `backend/.env`:

```env
DATABASE_URL=sqlite+aiosqlite:///./securedesk.db
DATABASE_URL_SYNC=sqlite:///./securedesk.db
SECRET_KEY=replace-with-a-local-development-secret
ENVIRONMENT=development
```

Run the API:

```bash
uvicorn main:app --reload
```

Useful URLs:

- API docs: `http://127.0.0.1:8000/docs`
- OpenAPI JSON: `http://127.0.0.1:8000/openapi.json`
- Health check: `http://127.0.0.1:8000/health`

Expected health response:

```json
{
  "status": "ok",
  "service": "SPS SecureDesk AI"
}
```

## Docker Compose

From the repository root:

```bash
docker compose up --build db mailhog backend
```

Local service URLs:

- Backend: `http://127.0.0.1:8000`
- Backend docs: `http://127.0.0.1:8000/docs`
- Mailhog UI: `http://127.0.0.1:8025`
- PostgreSQL: `localhost:5432`

Optional teammate services are included behind Compose profiles and should be used after those folders are added by their owners:

```bash
docker compose --profile email --profile ai up --build
```

## Environment Variables

Backend variables are documented in `backend/.env.example`.

| Variable | Required | Description |
| --- | --- | --- |
| `DATABASE_URL` | Yes | Async database URL used by FastAPI |
| `DATABASE_URL_SYNC` | Yes for Alembic | Sync database URL used by migrations |
| `SECRET_KEY` | Yes | JWT signing secret |
| `ALGORITHM` | No | JWT algorithm, defaults to `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No | JWT token lifetime |
| `UPLOAD_DIR` | No | Attachment storage path |
| `MAX_UPLOAD_SIZE_MB` | No | File upload limit, defaults to `10` |
| `ENVIRONMENT` | No | Use `development` locally and `production` in deployment |
| `CORS_ORIGINS` | No | Comma-separated allowed frontend origins |
| `SMTP_HOST` | Dev 2 | Outbound email host, Mailhog locally |
| `SMTP_PORT` | Dev 2 | Outbound email port |
| `IMAP_HOST` | Dev 2 | Inbound email host |
| `IMAP_USER` | Dev 2 | Inbound mailbox username |
| `IMAP_PASSWORD` | Dev 2 | Inbound mailbox password |
| `ANTHROPIC_API_KEY` | Dev 3 | AI service API key |
| `BACKEND_URL` | Dev 2/3 | Internal backend URL for service-to-service calls |

Never commit real `.env` files, database passwords, API keys, or production secrets.

## API Overview

### Public / Auth

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/health` | Backend health check |
| `POST` | `/auth/register` | Create a user account |
| `POST` | `/auth/login` | Login and receive a JWT token |
| `POST` | `/tickets` | Create a ticket from email, form, or chat |

### Ticket Operations

| Method | Endpoint | Description | Auth |
| --- | --- | --- | --- |
| `GET` | `/tickets` | List tickets visible to current user | Required |
| `GET` | `/tickets/{ticket_id}` | Get ticket detail with timeline and attachments | Required |
| `PATCH` | `/tickets/{ticket_id}` | Update status, category, priority, team, assignment, summary | Agent+ |
| `POST` | `/tickets/{ticket_id}/events` | Add timeline event | Auth optional for `email`/`chat`, otherwise required |
| `POST` | `/tickets/{ticket_id}/attachments` | Upload attachment | Auth optional |
| `POST` | `/tickets/{ticket_id}/approve` | Approve or reject high-risk ticket | Security Admin / Manager / Admin |
| `GET` | `/reports/summary` | Management report data | Manager / Admin |

### Planned AI Service Contract

The Dev 3 AI service owns this endpoint and the backend can integrate with it later:

| Method | Endpoint | Description |
| --- | --- | --- |
| `POST` | `/ai/classify` | Suggest category, priority, risk, and team |

## Example Requests

### Register an Agent

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

### Create a Portal Ticket

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

### Add an Email Timeline Event

```bash
curl -X POST http://127.0.0.1:8000/tickets/TICKET_UUID/events \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "email_received",
    "content": "Requester replied with logs.",
    "is_public": true,
    "channel": "email"
  }'
```

## Integration Contracts

All intake channels must create tickets through one backend endpoint:

```text
POST /tickets
```

| Developer | Module | Required `source` |
| --- | --- | --- |
| Dev 2 | Email pipeline | `email` |
| Dev 3 | AI chat escalation | `chat` |
| Dev 4 | Submit request form | `portal_form` |

Allowed ticket enums:

| Field | Values |
| --- | --- |
| `source` | `email`, `portal_form`, `chat` |
| `category` | `cloud`, `cybersecurity`, `identity_access`, `devops`, `internship_hr`, `general_it` |
| `priority` | `low`, `medium`, `high`, `critical` |
| `risk_level` | `standard`, `high` |
| `team` | `it`, `security`, `devops`, `hr`, `management` |
| `status` | `open`, `in_progress`, `waiting_approval`, `waiting_user`, `resolved`, `closed` |

Important workflow rules:

- `identity_access` tickets are automatically marked `risk_level=high`.
- High-risk tickets start as `status=waiting_approval`.
- Approved high-risk tickets move to `in_progress`.
- Rejected high-risk tickets move to `closed`.
- `cybersecurity` + `critical` tickets route to the `security` team.
- Timeline events are append-only.
- Audit logs record ticket actions and security events.

## Walkthrough Scenarios

Before final submission, the team should verify these scenarios end to end:

| # | Scenario | Reviewer Check |
| --- | --- | --- |
| 1 | Email laptop issue | Email creates `source=email` ticket, ack sent, email replies appear on same timeline, resolved notification sent |
| 2 | Web form VM down | Portal form creates `source=portal_form` ticket, file upload works, ticket appears in agent queue |
| 3 | AI chat VPN/admin access | Chat answers from KB, escalates admin access, creates `source=chat` ticket waiting for approval |
| 4 | Mixed channel | Email ticket later receives portal reply and upload on the same ticket ID |
| 5 | Security email | Phishing email becomes `category=cybersecurity`, `priority=critical`, `team=security` |
| 6 | Manager report | Manager sees high-risk and SLA metrics matching database tickets |

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

Daily Dev 1 workflow:

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
- Use a strong random `SECRET_KEY` in production.
- Review `CORS_ORIGINS` before deployment.
- Keep protected routes behind role checks.
- Use SQLAlchemy ORM queries instead of string-built SQL.
- Treat audit logs as append-only records.
- Security middleware logs suspicious request bodies and rejects unsafe payloads.
- Upload validation enforces file size and MIME checks server-side.

## Deployment Plan

Backend deployment target:

- Railway app for FastAPI backend
- Railway PostgreSQL plugin for production database
- Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

Frontend deployment target:

- Vercel app for React frontend
- `VITE_API_URL` points to the Railway backend URL

Production checklist:

- `DATABASE_URL` points to managed PostgreSQL.
- `SECRET_KEY` is a random production-only value.
- `ENVIRONMENT=production`.
- `CORS_ORIGINS` only includes deployed frontend URLs.
- No `.env` files or secrets are committed to GitHub.
- `/docs` and `/health` are reachable on the deployed backend.

## Team

| Role | Owner | Responsibility |
| --- | --- | --- |
| Dev 1 / Team Lead | Muhammad Osama | Backend, ticket engine, API contract, Docker Compose, README, deployment coordination |
| Dev 2 | Email Pipeline | IMAP polling, thread resolver, SMTP notifications, email templates |
| Dev 3 | AI Layer | KB search, chat assistant, classifier, summarizer, escalation bridge |
| Dev 4 | Frontend Portal | React UI, submit form, chat widget, agent queue, dashboards |
