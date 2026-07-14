"""Fix CHECK constraint names that were never actually dropped by the previous migration.

Revision ID: 202607140004
Revises: 202607130003
Create Date: 2026-07-14

Migration 202607130003 was already applied to the live (production) database, but its
PostgreSQL branch tried to DROP constraints named "tickets_status_check" / "ck_tickets_status"
and "tickets_source_check" / "ck_tickets_source" etc. Those names were WRONG guesses -- the
constraints actually created by SQLAlchemy's SQLEnum(native_enum=False) use the explicit
`name=` argument from the models:
- tickets.status       -> "ticket_status"
- tickets.source       -> "ticket_source"
- timeline_events.event_type -> "timeline_event_type"

Because the DROP used the wrong names (with IF EXISTS, so it silently no-op'd), the real
constraints were never relaxed, and 'duplicate' / 'escalated' (and the related source/event
values) continued to be rejected. Editing the already-applied 202607130003 file does NOT
re-run it, so this dedicated migration performs the actual fix on the live database.

It drops the REAL constraints (ticket_status, ticket_source, timeline_event_type) and recreates
them with the correct allowed values including 'duplicate' and 'escalated'.
"""

from alembic import op
import sqlalchemy as sa

revision = "202607140004"
down_revision = "202607130003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    is_postgresql = bind.dialect.name == "postgresql"

    if is_postgresql:
        # tickets.status -> "ticket_status"
        op.execute("ALTER TABLE tickets DROP CONSTRAINT IF EXISTS ticket_status")
        op.execute("""
            ALTER TABLE tickets ADD CONSTRAINT ticket_status
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

        # tickets.source -> "ticket_source"
        op.execute("ALTER TABLE tickets DROP CONSTRAINT IF EXISTS ticket_source")
        op.execute("""
            ALTER TABLE tickets ADD CONSTRAINT ticket_source
            CHECK (source::text = ANY (ARRAY[
                'email'::text,
                'portal_form'::text,
                'chat'::text,
                'form'::text,
                'ai_chat'::text,
                'dashboard'::text
            ]))
        """)

        # timeline_events.event_type -> "timeline_event_type"
        op.execute("ALTER TABLE timeline_events DROP CONSTRAINT IF EXISTS timeline_event_type")
        op.execute("""
            ALTER TABLE timeline_events ADD CONSTRAINT timeline_event_type
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

    # For SQLite (local/dev) the relaxed constraints are already in place from
    # 202607130003 (which rebuilds the tables). Nothing to do here, but we keep
    # the branch explicit for safety/clarity.
    return


def downgrade() -> None:
    # We do not restore the stricter (broken) constraints, because doing so would
    # immediately reject the 'duplicate' / 'escalated' values that the application
    # now relies on. Leave the relaxed constraints in place.
    pass