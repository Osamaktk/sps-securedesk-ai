# SPS SecureDesk AI Frontend

SPS SecureDesk AI is a frontend-only enterprise helpdesk prototype for unified
email, portal form, and AI chat support. It demonstrates requester, service
desk agent, security, manager, and administrator workflows using realistic mock
data and service placeholders.

The current implementation does not connect to a backend, AI provider, email
service, identity provider, or persistent database.

## Tech Stack

- React 18
- Vite 5
- React Router 6
- Tailwind CSS 3
- Custom SPS theme and responsive CSS
- Static mock data and asynchronous mock services

## Install And Run

Requirements: a current Node.js LTS release and npm.

```bash
cd frontend
npm install
npm run dev
```

Vite prints the local development URL after startup.

Create a production build with:

```bash
npm run build
```

Preview that build locally with:

```bash
npm run preview
```

## Available Pages

| Area | Route | Purpose |
| --- | --- | --- |
| Authentication | `/login` | Mock sign-in screen |
| Requester | `/requester` | Requester overview and quick actions |
| Requester | `/requester/submit` | Submit a mock portal request |
| Requester | `/requester/tickets` | Track requester tickets from every source |
| Requester | `/requester/ai-chat` | Full SecureDesk AI chat workspace |
| Agent | `/agent` | Unified service desk operations dashboard |
| Agent | `/agent/queue` | Searchable and filterable ticket queue |
| Agent | `/agent/tickets/:ticketId` | Unified ticket detail and timeline |
| Security | `/security` | Security operations overview |
| Security | `/security/approvals` | Human approval queue for sensitive access |
| Manager | `/manager` | Manager operations overview |
| Manager | `/manager/reports` | Mock operational and audit reports |
| Admin | `/admin` | Administration overview |
| Admin | `/admin/users` | User management placeholder |
| Admin | `/admin/knowledge-base` | Knowledge base management placeholder |
| Admin | `/admin/categories` | Category management placeholder |
| Admin | `/admin/sla-settings` | SLA configuration placeholder |
| Admin | `/admin/email-settings` | Email intake configuration placeholder |

All authenticated-area routes use the shared application shell and include the
global floating SecureDesk AI widget.

## Folder Structure

```text
frontend/
|-- public/                  Static logo and favicon assets
|-- src/
|   |-- assets/images/      Frontend image assets
|   |-- components/
|   |   |-- chat/           Floating and full-page chat components
|   |   |-- common/         App shell and reusable UI components
|   |   |-- dashboard/      Agent dashboard components
|   |   |-- forms/          Request form and upload components
|   |   `-- tickets/        Queue, detail, badges, and timeline components
|   |-- data/               Tickets, chat, reports, and users mock data
|   |-- pages/              Role-based route pages
|   |-- routes/             React Router configuration
|   |-- services/           Mock asynchronous service contracts
|   |-- styles/             Theme, global, and responsive styles
|   |-- utils/              Shared frontend utilities
|   |-- App.jsx
|   `-- main.jsx
|-- package.json
`-- README.md
```

## Mock Data And Behavior

- `src/data/mockTickets.js` contains realistic tickets, attachments, AI
  summaries, source channels, SLA details, and unified timeline events.
- `src/data/mockChat.js` provides the welcome conversation, citations, and
  escalation examples.
- `src/data/mockReports.js` and `src/data/mockUsers.js` support dashboards,
  reports, approvals, and administration views.
- Service functions return promises to model future API usage while keeping all
  changes in browser memory. Reloading the application resets mock changes.
- Ticket creation, comments, attachments, approvals, status updates, and chat
  responses are demonstrations only.

## Future Backend Integration

The files in `src/services/` define the intended frontend integration boundary:

- `api.js`: shared request client and backend configuration
- `authService.js`: authentication, session, and current-user APIs
- `ticketService.js`: ticket search, creation, comments, attachments, and status
- `chatService.js`: approved knowledge-base chat and ticket escalation
- `reportService.js`: dashboard and reporting data
- `uploadService.js`: secured file upload

When backend work begins, replace the mock implementations behind these
service contracts and add authorization, validation, error mapping, and
persistent storage. Sensitive access approvals must remain human-controlled.

## UI And Accessibility

The interface uses SPS blue and navy theme variables, reusable cards, buttons,
badges, responsive layouts, keyboard focus styles, labeled form controls,
table captions, loading/error/empty states, and reduced-motion support.

## Scope Guardrails

- No backend API calls
- No real AI API calls
- No real email delivery or intake
- No production authentication or authorization
- No persistent uploads or ticket changes
