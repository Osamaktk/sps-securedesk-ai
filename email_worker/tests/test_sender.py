"""Tests for the SMTP sender module."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from email_worker.smtp.sender import EmailSender
from email_worker.models.email_models import EmailTemplateData


class TestEmailSender:
    """Tests for EmailSender."""

    def test_generate_message_id_format(self):
        sender = EmailSender()
        mid = sender._generate_message_id()
        assert "@sps.com" in mid
        assert "<" in mid
        assert ">" in mid

    def test_generate_message_id_with_ticket_id(self):
        sender = EmailSender()
        mid = sender._generate_message_id("SPS-2026-001")
        assert "SPS-2026-001" in mid
        assert "@sps.com" in mid

    def test_build_message_structure(self):
        sender = EmailSender()
        msg, mid = sender._build_message(
            to_email="user@test.com",
            subject="Test Subject",
            html_body="<html><body>Hi</body></html>",
            plain_text_body="Hi",
            message_id="<test@sps.com>",
        )
        assert msg["From"] == "SPS Helpdesk <helpdesk@sps.com>"
        assert msg["To"] == "user@test.com"
        assert msg["Subject"] == "Test Subject"
        assert msg["Message-ID"] == "<test@sps.com>"
        assert msg.get_content_type() == "multipart/alternative"

    def test_build_message_with_in_reply_to(self):
        sender = EmailSender()
        msg, mid = sender._build_message(
            to_email="user@test.com",
            subject="Re: Test",
            html_body="<p>Reply</p>",
            plain_text_body="Reply",
            message_id="<reply@sps.com>",
            in_reply_to="<original@sps.com>",
        )
        assert msg["In-Reply-To"] == "<original@sps.com>"

    def test_render_template_fallback_on_error(self):
        sender = EmailSender()
        data = EmailTemplateData(
            ticket_id="SPS-2026-999",
            subject="Fallback test",
        )
        result = sender._render_template("nonexistent_template.html", data)
        assert "SPS-2026-999" in result
        assert "Fallback test" in result