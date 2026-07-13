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
    
    if bind.dialect.name == "postgresql":
        # Directly drop and recreate CHECK constraints with all values
        # This handles the case where native_enum=False creates CHECK constraints instead of native types
        
        # ticket_status constraint - includes duplicate and escalated
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
        
        # ticket_source constraint - includes form, ai_chat, dashboard  
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
        
        # timeline_event_type constraint - includes duplicate_attempt, email_reply, escalated
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


def downgrade() -> None:
    pass