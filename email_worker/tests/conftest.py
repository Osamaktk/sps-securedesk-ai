"""Shared pytest fixtures for email worker tests."""

import tempfile
from typing import Generator

import pytest

from email_worker.storage.message_store import MessageStore


@pytest.fixture
def temp_store(tmp_path) -> Generator[MessageStore, None, None]:
    """Provide a fresh MessageStore backed by a temp directory."""
    store = MessageStore(
        file_path=str(tmp_path / "test_message_store.json")
    )
    yield store


@pytest.fixture
def sample_email_bytes() -> bytes:
    """Return raw RFC 822 bytes for a simple plain-text email."""
    return (
        b"From: Test User <test@example.com>\r\n"
        b"To: helpdesk@sps.com\r\n"
        b"Subject: My computer is broken\r\n"
        b"Message-ID: <abc123@example.com>\r\n"
        b"Date: Mon, 15 Jun 2026 10:00:00 +0000\r\n"
        b"Content-Type: text/plain; charset=UTF-8\r\n"
        b"\r\n"
        b"My computer is not turning on. Please help.\r\n"
    )


@pytest.fixture
def sample_html_email_bytes() -> bytes:
    """Return raw RFC 822 bytes for a multipart HTML+text email."""
    return (
        b"From: Test User <test@example.com>\r\n"
        b"To: helpdesk@sps.com\r\n"
        b"Subject: Password reset issue\r\n"
        b"Message-ID: <def456@example.com>\r\n"
        b"In-Reply-To: <ghi789@sps.com>\r\n"
        b"Date: Mon, 15 Jun 2026 11:00:00 +0000\r\n"
        b"Content-Type: multipart/alternative; boundary=\"boundary123\"\r\n"
        b"\r\n"
        b"--boundary123\r\n"
        b"Content-Type: text/plain; charset=UTF-8\r\n"
        b"\r\n"
        b"I still cannot reset my password.\r\n"
        b"--boundary123\r\n"
        b"Content-Type: text/html; charset=UTF-8\r\n"
        b"\r\n"
        b"<html><body><p>I still <b>cannot</b> reset my password.</p></body></html>\r\n"
        b"--boundary123--\r\n"
    )


@pytest.fixture
def sample_ticket_email_bytes() -> bytes:
    """Return raw RFC 822 bytes for a reply email with a ticket tag in the subject."""
    return (
        b"From: Customer <customer@corp.com>\r\n"
        b"To: helpdesk@sps.com\r\n"
        b"Subject: Re: [SPS-2026-042] VPN access request\r\n"
        b"Message-ID: <reply123@corp.com>\r\n"
        b"In-Reply-To: <sps-outbound-sp42@sps.com>\r\n"
        b"Date: Tue, 16 Jun 2026 09:00:00 +0000\r\n"
        b"Content-Type: text/plain; charset=UTF-8\r\n"
        b"\r\n"
        b"Thank you, the VPN is working now.\r\n"
    )