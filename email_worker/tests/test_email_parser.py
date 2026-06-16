"""Tests for the email parser module."""

import pytest
from email_worker.imap.parser import parse_email, _decode_mime_header


class TestDecodeMimeHeader:
    """Tests for MIME header decoding."""

    def test_returns_empty_for_none(self):
        assert _decode_mime_header("") == ""

    def test_decodes_plain_ascii(self):
        assert _decode_mime_header("Hello World") == "Hello World"


class TestParseEmail:
    """Tests for parse_email function."""

    def test_returns_none_for_empty_content(self):
        assert parse_email(b"") is None

    def test_returns_none_for_invalid_bytes(self):
        assert parse_email(b"\x00\x01\x02\x03") is None

    def test_parses_plain_text_email(self, sample_email_bytes):
        parsed = parse_email(sample_email_bytes)
        assert parsed is not None
        assert parsed.from_address == "test@example.com"
        assert parsed.subject == "My computer is broken"
        assert parsed.message_id == "<abc123@example.com>"
        assert "not turning on" in parsed.plain_text_body
        assert len(parsed.attachments) == 0

    def test_parses_multipart_email(self, sample_html_email_bytes):
        parsed = parse_email(sample_html_email_bytes)
        assert parsed is not None
        assert parsed.from_address == "test@example.com"
        assert parsed.subject == "Password reset issue"
        assert "cannot reset my password" in parsed.plain_text_body
        assert "<b>cannot</b>" in parsed.html_body
        assert parsed.in_reply_to == "<ghi789@sps.com>"

    def test_extracts_ticket_reply_email(self, sample_ticket_email_bytes):
        parsed = parse_email(sample_ticket_email_bytes)
        assert parsed is not None
        assert parsed.from_address == "customer@corp.com"
        assert "[SPS-2026-042]" in parsed.subject
        assert "VPN is working" in parsed.plain_text_body
        assert parsed.in_reply_to == "<sps-outbound-sp42@sps.com>"