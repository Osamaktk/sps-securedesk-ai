"""Tests for the thread resolver module."""

import pytest
from unittest.mock import patch

from email_worker.models.email_models import ParsedEmail
from email_worker.thread.resolver import (
    extract_ticket_tag,
    resolve_thread,
)


class TestExtractTicketTag:
    """Tests for subject tag extraction."""

    def test_extracts_ticket_id_from_subject(self):
        assert extract_ticket_tag("[SPS-2026-001] Password reset") == "SPS-2026-001"

    def test_extracts_large_ticket_number(self):
        assert extract_ticket_tag("Re: [SPS-2026-1000] Issue") == "SPS-2026-1000"

    def test_returns_none_for_clean_subject(self):
        assert extract_ticket_tag("My computer is broken") is None

    def test_returns_none_for_empty_subject(self):
        assert extract_ticket_tag("") is None


class TestResolveThread:
    """Tests for thread resolution logic."""

    def test_new_ticket_via_subject_tag(self):
        email = ParsedEmail(
            from_address="user@example.com",
            subject="[SPS-2026-001] Password reset",
            message_id="<msg1@ex.com>",
        )
        result = resolve_thread(email)
        assert result == ("reply", "SPS-2026-001")

    def test_new_ticket_via_in_reply_to(self):
        email = ParsedEmail(
            from_address="user@example.com",
            subject="Re: Help please",
            message_id="<msg2@ex.com>",
            in_reply_to="<sps-sp42@ex.com>",
        )
        with patch(
            "email_worker.thread.resolver.message_store"
        ) as mock_store:
            mock_store.lookup_message_id.return_value = "SPS-2026-042"
            result = resolve_thread(email)
        assert result == ("reply", "SPS-2026-042")

    def test_new_ticket_no_match(self):
        email = ParsedEmail(
            from_address="user@example.com",
            subject="My computer is broken",
            message_id="<msg3@ex.com>",
        )
        with patch(
            "email_worker.thread.resolver.message_store"
        ) as mock_store:
            mock_store.lookup_message_id.return_value = None
            result = resolve_thread(email)
        assert result == ("new", None)