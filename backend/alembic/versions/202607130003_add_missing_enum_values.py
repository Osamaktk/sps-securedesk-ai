"""Add missing enum values for duplicate detection and escalation.

Revision ID: 202607130003
Revises: 202606230002
Create Date: 2026-07-13

This migration adds the missing enum values that were added to the codebase but not to the database:
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
    # Add missing ticket_status enum values
    op.execute("ALTER TYPE ticket_status ADD VALUE IF NOT EXISTS 'duplicate'")
    op.execute("ALTER TYPE ticket_status ADD VALUE IF NOT EXISTS 'escalated'")
    
    # Add missing ticket_source enum values
    op.execute("ALTER TYPE ticket_source ADD VALUE IF NOT EXISTS 'form'")
    op.execute("ALTER TYPE ticket_source ADD VALUE IF NOT EXISTS 'ai_chat'")
    op.execute("ALTER TYPE ticket_source ADD VALUE IF NOT EXISTS 'dashboard'")
    
    # Add missing timeline_event_type enum values
    op.execute("ALTER TYPE timeline_event_type ADD VALUE IF NOT EXISTS 'duplicate_attempt'")
    op.execute("ALTER TYPE timeline_event_type ADD VALUE IF NOT EXISTS 'email_reply'")
    op.execute("ALTER TYPE timeline_event_type ADD VALUE IF NOT EXISTS 'escalated'")


def downgrade() -> None:
    # PostgreSQL doesn't support removing enum values directly, so we leave this empty
    pass