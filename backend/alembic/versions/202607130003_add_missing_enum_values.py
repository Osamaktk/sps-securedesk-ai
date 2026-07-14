"""Add missing enum values to CHECK constraints for duplicate detection.

Revision ID: 202607130003
Revises: 202606230002
Create Date: 2026-07-13

This migration adds the missing enum values that were added to the codebase but not to the database.
Since the models use native_enum=False, the values are enforced via CHECK constraints, not
native PostgreSQL enum types. This migration drops and recreates the CHECK constraints with
all required values:
- ticket_status: 'duplicate', 'escalated' (missing in DB)
- ticket_source: 'form', 'ai_chat', 'dashboard' (missing in DB)
- timeline_event_type: 'duplicate_attempt', 'email_reply', 'escalated' (missing in DB)
"""

from alembic import op
import sqlalchemy as sa

revision = "202607130003"
down_revision = "202606230002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    is_postgresql = bind.dialect.name == "postgresql"

    # The enum columns use native_enum=False, so values are enforced via CHECK
    # constraints. These must be relaxed on EVERY backend (including SQLite, the
    # documented local/dev database) so statuses/event types introduced for
    # duplicate detection are accepted. Previously this block was gated to
    # PostgreSQL only, which left SQLite databases rejecting 'duplicate' /
    # 'duplicate_attempt' and caused ticket creation to fail (HTTP 500) on the
    # duplicate-submission path.

    if is_postgresql:
        # PostgreSQL supports dropping and re-adding CHECK constraints directly.
        op.execute("ALTER TABLE tickets DROP CONSTRAINT IF EXISTS ck_tickets_status")
        op.execute("ALTER TABLE tickets DROP CONSTRAINT IF EXISTS tickets_status_check")
        op.execute("""
            ALTER TABLE tickets ADD CONSTRAINT tickets_status_check
            CHECK (status::text = ANY (ARRAY[
                'open'::text,
                'in_progress'::text,
                'waiting_approval'::text,
                'waiting_user'::text,
                'resolved'::text,
                'duplicate'::text,
                'closed'::text,
                'escalated'::text
            ]))
        """)

        op.execute("ALTER TABLE tickets DROP CONSTRAINT IF EXISTS ck_tickets_source")
        op.execute("ALTER TABLE tickets DROP CONSTRAINT IF EXISTS tickets_source_check")
        op.execute("""
            ALTER TABLE tickets ADD CONSTRAINT tickets_source_check
            CHECK (source::text = ANY (ARRAY[
                'email'::text,
                'portal_form'::text,
                'chat'::text,
                'form'::text,
                'ai_chat'::text,
                'dashboard'::text
            ]))
        """)

        op.execute("ALTER TABLE timeline_events DROP CONSTRAINT IF EXISTS ck_timeline_events_event_type")
        op.execute("ALTER TABLE timeline_events DROP CONSTRAINT IF EXISTS timeline_events_event_type_check")
        op.execute("""
            ALTER TABLE timeline_events ADD CONSTRAINT timeline_events_event_type_check
            CHECK (event_type::text = ANY (ARRAY[
                'ticket_created'::text,
                'email_received'::text,
                'agent_reply_portal'::text,
                'agent_reply_email'::text,
                'internal_note'::text,
                'status_change'::text,
                'field_update'::text,
                'approval_requested'::text,
                'approval_resolved'::text,
                'file_uploaded'::text,
                'chat_escalation'::text,
                'ai_classified'::text,
                'duplicate_attempt'::text,
                'email_reply'::text,
                'escalated'::text
            ]))
        """)
        return

    # SQLite cannot DROP/ADD table-level CHECK constraints in place. The only
    # supported way is to rebuild the table: create a new table with the relaxed
    # constraints, copy the existing rows, drop the old table, and rename.
    op.execute("PRAGMA foreign_keys=OFF")

    TICKETS_COLUMNS = [
        "id", "ticket_number", "source", "requester_id", "requester_email",
        "subject", "description", "category", "priority", "risk_level",
        "team", "status", "assigned_agent_id", "ai_summary", "sla_due_at",
        "created_at", "updated_at",
    ]
    EVENT_COLUMNS = [
        "id", "ticket_id", "event_type", "actor_id", "actor_email",
        "content", "is_public", "channel", "created_at",
    ]

    op.execute("""
        CREATE TABLE tickets_new (
            id CHAR(32) NOT NULL,
            ticket_number VARCHAR(20) NOT NULL,
            source VARCHAR(11) NOT NULL,
            requester_id CHAR(32),
            requester_email VARCHAR(255) NOT NULL,
            subject TEXT NOT NULL,
            description TEXT,
            category VARCHAR(15) NOT NULL,
            priority VARCHAR(8) NOT NULL,
            risk_level VARCHAR(8) NOT NULL,
            team VARCHAR(10) NOT NULL,
            status VARCHAR(16) NOT NULL,
            assigned_agent_id CHAR(32),
            ai_summary TEXT,
            sla_due_at DATETIME,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
            PRIMARY KEY (id),
            FOREIGN KEY(assigned_agent_id) REFERENCES users (id),
            FOREIGN KEY(requester_id) REFERENCES users (id),
            UNIQUE (ticket_number),
            CONSTRAINT ticket_source CHECK (source IN ('email', 'portal_form', 'chat', 'form', 'ai_chat', 'dashboard')),
            CONSTRAINT ticket_category CHECK (category IN ('cloud', 'cybersecurity', 'identity_access', 'devops', 'internship_hr', 'general_it')),
            CONSTRAINT ticket_priority CHECK (priority IN ('low', 'medium', 'high', 'critical')),
            CONSTRAINT risk_level CHECK (risk_level IN ('standard', 'high')),
            CONSTRAINT ticket_team CHECK (team IN ('it', 'security', 'devops', 'hr', 'management')),
            CONSTRAINT ticket_status CHECK (status IN ('open', 'in_progress', 'waiting_approval', 'waiting_user', 'resolved', 'duplicate', 'closed', 'escalated'))
        )
    """)
    op.execute(
        f"INSERT INTO tickets_new ({', '.join(TICKETS_COLUMNS)}) "
        f"SELECT {', '.join(TICKETS_COLUMNS)} FROM tickets"
    )
    op.execute("DROP TABLE tickets")
    op.execute("ALTER TABLE tickets_new RENAME TO tickets")

    op.execute("""
        CREATE TABLE timeline_events_new (
            id CHAR(32) NOT NULL,
            ticket_id CHAR(32) NOT NULL,
            event_type VARCHAR(20) NOT NULL,
            actor_id CHAR(32),
            actor_email VARCHAR(255),
            content TEXT,
            is_public BOOLEAN NOT NULL,
            channel VARCHAR(20),
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
            FOREIGN KEY(actor_id) REFERENCES users (id),
            FOREIGN KEY(ticket_id) REFERENCES tickets (id) ON DELETE CASCADE,
            CONSTRAINT timeline_event_type CHECK (event_type IN (
                'ticket_created', 'email_received', 'agent_reply_portal',
                'agent_reply_email', 'internal_note', 'status_change',
                'field_update', 'approval_requested', 'approval_resolved',
                'file_uploaded', 'chat_escalation', 'ai_classified',
                'duplicate_attempt', 'email_reply', 'escalated'
            ))
        )
    """)
    op.execute(
        f"INSERT INTO timeline_events_new ({', '.join(EVENT_COLUMNS)}) "
        f"SELECT {', '.join(EVENT_COLUMNS)} FROM timeline_events"
    )
    op.execute("DROP TABLE timeline_events")
    op.execute("ALTER TABLE timeline_events_new RENAME TO timeline_events")

    op.execute("PRAGMA foreign_keys=ON")


def downgrade() -> None:
    pass