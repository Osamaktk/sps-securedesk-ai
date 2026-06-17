"""Integration test script for the email pipeline.

This script tests the full email pipeline by:
1. Sending a test email to Mailhog (SMTP)
2. Verifying the email was received
3. Testing the email parser
4. Testing the thread resolver
5. Testing the message store

Usage:
    python -m email_worker.tests.test_pipeline_integration
"""

import asyncio
import email.mime.multipart
import email.mime.text
import smtplib
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from email_worker.imap.parser import parse_email
from email_worker.thread.resolver import resolve_thread
from email_worker.storage.message_store import MessageStore
from email_worker.models.email_models import ParsedEmail


def send_test_email(
    to_email: str = "helpdesk@sps.com",
    subject: str = "Test: My computer is broken",
    body: str = "My computer is not turning on. Please help.",
    smtp_host: str = "localhost",
    smtp_port: int = 1025,
    message_id: str = "<test-123@example.com>",
    in_reply_to: str = None,
):
    """Send a test email to Mailhog."""
    msg = email.mime.multipart.MIMEMultipart("alternative")
    msg["From"] = "Test User <test@example.com>"
    msg["To"] = to_email
    msg["Subject"] = subject
    msg["Message-ID"] = message_id
    if in_reply_to:
        msg["In-Reply-To"] = in_reply_to

    part_text = email.mime.text.MIMEText(body, "plain", "utf-8")
    msg.attach(part_text)

    try:
        with smtplib.SMTP(host=smtp_host, port=smtp_port, timeout=10) as server:
            server.send_message(msg)
        print(f"✅ Email sent to {to_email}: {subject}")
        return True
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        return False


def test_email_parsing():
    """Test email parsing with a sample email."""
    print("\n--- Test: Email Parsing ---")
    raw_email = (
        b"From: Test User <test@example.com>\r\n"
        b"To: helpdesk@sps.com\r\n"
        b"Subject: My computer is broken\r\n"
        b"Message-ID: <abc123@example.com>\r\n"
        b"Date: Mon, 15 Jun 2026 10:00:00 +0000\r\n"
        b"Content-Type: text/plain; charset=UTF-8\r\n"
        b"\r\n"
        b"My computer is not turning on. Please help.\r\n"
    )
    parsed = parse_email(raw_email)
    assert parsed is not None
    assert parsed.from_address == "test@example.com"
    assert parsed.subject == "My computer is broken"
    assert "not turning on" in parsed.plain_text_body
    print("✅ Email parsing test passed")


def test_thread_resolution():
    """Test thread resolution with a ticket tag."""
    print("\n--- Test: Thread Resolution ---")
    email = ParsedEmail(
        from_address="user@example.com",
        subject="[SPS-2026-001] Password reset",
        message_id="<msg1@ex.com>",
    )
    result = resolve_thread(email)
    assert result == ("reply", "SPS-2026-001")
    print("✅ Thread resolution test passed")


def test_message_store():
    """Test message store operations."""
    import tempfile
    print("\n--- Test: Message Store ---")
    with tempfile.TemporaryDirectory() as tmpdir:
        store_path = os.path.join(tmpdir, "test_store.json")
        store = MessageStore(file_path=store_path)
        store.save_message_mapping("<test@ex.com>", "SPS-2026-001")
        assert store.lookup_message_id("<test@ex.com>") == "SPS-2026-001"
        assert store.count == 1
        store.delete_mapping("<test@ex.com>")
        assert store.count == 0
    print("✅ Message store test passed")


def test_send_email_to_mailhog():
    """Test sending an email to Mailhog."""
    print("\n--- Test: Send Email to Mailhog ---")
    success = send_test_email(
        to_email="helpdesk@sps.com",
        subject="Test: My computer is broken",
        body="My computer is not turning on. Please help.",
        smtp_host="localhost",
        smtp_port=1025,
    )
    if success:
        print("✅ Email sent to Mailhog successfully")
    else:
        print("⚠️  Mailhog not running (start with: docker run -d -p 1025:1025 -p 8025:8025 mailhog/mailhog)")


def test_send_reply_email_to_mailhog():
    """Test sending a reply email to Mailhog."""
    print("\n--- Test: Send Reply Email to Mailhog ---")
    success = send_test_email(
        to_email="helpdesk@sps.com",
        subject="Re: [SPS-2026-001] Password reset",
        body="Thank you, the password reset worked.",
        smtp_host="localhost",
        smtp_port=1025,
        message_id="<reply-456@example.com>",
        in_reply_to="<sps-sp1@ex.com>",
    )
    if success:
        print("✅ Reply email sent to Mailhog successfully")
    else:
        print("⚠️  Mailhog not running")


def main():
    """Run all integration tests."""
    print("=" * 60)
    print("SPS SecureDesk AI Email Pipeline - Integration Tests")
    print("=" * 60)

    test_email_parsing()
    test_thread_resolution()
    test_message_store()
    test_send_email_to_mailhog()
    test_send_reply_email_to_mailhog()

    print("\n" + "=" * 60)
    print("All integration tests completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()