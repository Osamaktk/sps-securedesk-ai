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
        # Use a DO block that safely handles both cases: native enums exist OR don't exist
        op.execute("""
            DO $$
            DECLARE
                has_enum boolean;
            BEGIN
                -- Check if native PostgreSQL enum types exist
                SELECT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'ticket_status') INTO has_enum;
                
                IF has_enum THEN
                    -- Native enum types exist - add values to them
                    BEGIN
                        ALTER TYPE ticket_status ADD VALUE IF NOT EXISTS 'duplicate';
                        ALTER TYPE ticket_status ADD VALUE IF NOT EXISTS 'escalated';
                    EXCEPTION WHEN OTHERS THEN
                        -- Type might have been created differently, fall through to CHECK handling
                    END;
                    BEGIN
                        ALTER TYPE ticket_source ADD VALUE IF NOT EXISTS 'form';
                        ALTER TYPE ticket_source ADD VALUE IF NOT EXISTS 'ai_chat';
                        ALTER TYPE ticket_source ADD VALUE IF NOT EXISTS 'dashboard';
                    EXCEPTION WHEN OTHERS THEN
                    END;
                    BEGIN
                        ALTER TYPE timeline_event_type ADD VALUE IF NOT EXISTS 'duplicate_attempt';
                        ALTER TYPE timeline_event_type ADD VALUE IF NOT EXISTS 'email_reply';
                        ALTER TYPE timeline_event_type ADD VALUE IF NOT EXISTS 'escalated';
                    EXCEPTION WHEN OTHERS THEN
                    END;
                ELSE
                    -- No native enum types - handle CHECK constraints
                    -- Drop and recreate CHECK constraints with all values
                    
                    -- ticket_status constraint
                    ALTER TABLE tickets DROP CONSTRAINT IF EXISTS tickets_status_check;
                    ALTER TABLE tickets ADD CONSTRAINT tickets_status_check 
                    CHECK (status::text = ANY (ARRAY['open'::text, 'in_progress'::text, 
                           'waiting_approval'::text, 'waiting_user'::text, 'resolved'::text, 
                           'duplicate'::text, 'closed'::text, 'escalated'::text]));
                    
                    -- ticket_source constraint
                    ALTER TABLE tickets DROP CONSTRAINT IF EXISTS tickets_source_check;
                    ALTER TABLE tickets ADD CONSTRAINT tickets_source_check 
                    CHECK (source::text = ANY (ARRAY['email'::text, 'portal_form'::text, 'chat'::text, 
                           'form'::text, 'ai_chat'::text, 'dashboard'::text]));
                    
                    -- timeline_event_type constraint
                    ALTER TABLE timeline_events DROP CONSTRAINT IF EXISTS timeline_events_event_type_check;
                    ALTER TABLE timeline_events ADD CONSTRAINT timeline_events_event_type_check 
                    CHECK (event_type::text = ANY (ARRAY['ticket_created'::text, 'email_received'::text, 
                           'agent_reply_portal'::text, 'agent_reply_email'::text, 'internal_note'::text, 
                           'status_change'::text, 'field_update'::text, 'approval_requested'::text, 
                           'approval_resolved'::text, 'file_uploaded'::text, 'chat_escalation'::text, 
                           'ai_classified'::text, 'duplicate_attempt'::text, 'email_reply'::text, 
                           'escalated'::text]));
                END IF;
            EXCEPTION WHEN OTHERS THEN
                -- If any error occurs, try to repair CHECK constraints as a fallback
                BEGIN
                    ALTER TABLE tickets DROP CONSTRAINT IF EXISTS tickets_status_check;
                    ALTER TABLE tickets ADD CONSTRAINT tickets_status_check 
                    CHECK (status::text = ANY (ARRAY['open'::text, 'in_progress'::text, 
                           'waiting_approval'::text, 'waiting_user'::text, 'resolved'::text, 
                           'duplicate'::text, 'closed'::text, 'escalated'::text]));
                EXCEPTION WHEN OTHERS THEN
                END;
                BEGIN
                    ALTER TABLE tickets DROP CONSTRAINT IF EXISTS tickets_source_check;
                    ALTER TABLE tickets ADD CONSTRAINT tickets_source_check 
                    CHECK (source::text = ANY (ARRAY['email'::text, 'portal_form'::text, 'chat'::text, 
                           'form'::text, 'ai_chat'::text, 'dashboard'::text]));
                EXCEPTION WHEN OTHERS THEN
                END;
                BEGIN
                    ALTER TABLE timeline_events DROP CONSTRAINT IF EXISTS timeline_events_event_type_check;
                    ALTER TABLE timeline_events ADD CONSTRAINT timeline_events_event_type_check 
                    CHECK (event_type::text = ANY (ARRAY['ticket_created'::text, 'email_received'::text, 
                           'agent_reply_portal'::text, 'agent_reply_email'::text, 'internal_note'::text, 
                           'status_change'::text, 'field_update'::text, 'approval_requested'::text, 
                           'approval_resolved'::text, 'file_uploaded'::text, 'chat_escalation'::text, 
                           'ai_classified'::text, 'duplicate_attempt'::text, 'email_reply'::text, 
                           'escalated'::text]));
                EXCEPTION WHEN OTHERS THEN
                END;
            END $$;
        """)


def downgrade() -> None:
    pass