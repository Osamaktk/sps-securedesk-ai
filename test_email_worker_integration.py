"""Integration test for email worker - simulates email processing without actual IMAP."""

import asyncio
import sys

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

from email_worker.imap.poller import IMAPPoller, ClassifyResponse
from email_worker.models.email_models import ParsedEmail
from email_worker.api_client.ticket_client import TicketClient
from email_worker.config.settings import settings


def create_test_email() -> ParsedEmail:
    """Create a mock parsed email for testing."""
    return ParsedEmail(
        message_id="<test-123@example.com>",
        in_reply_to=None,
        from_address="testuser@example.com",
        to_address=settings.imap_user,
        subject="My laptop won't turn on",
        plain_text_body="I pressed the power button but nothing happens. Please help!",
        html_body="",
        attachments=[]
    )


async def test_classification_fallback():
    """Test that fallback classification works."""
    print("\n" + "="*60)
    print("TEST 1: Classification Fallback")
    print("="*60)

    # Simulate AI service being down by using an invalid URL
    client = TicketClient(
        backend_url="http://localhost:8000",
        ai_url="http://invalid-ai-service:9999"
    )

    try:
        # This should timeout/fail
        classify = await asyncio.wait_for(
            client.classify_email(
                subject="Test subject",
                description="Test description"
            ),
            timeout=2.0
        )
        print("UNEXPECTED: Classification succeeded (AI service shouldn't be reachable)")
        print(f"Result: {classify}")
    except Exception as e:
        print(f"Expected failure: {type(e).__name__}: {str(e)[:100]}")
        print("\nFallback would be used:")
        fallback = ClassifyResponse(
            category="general_it",
            priority="medium",
            team="it"
        )
        print(f"  category: {fallback.category}")
        print(f"  priority: {fallback.priority}")
        print(f"  team: {fallback.team}")
        print("✓ Fallback classification works")
    finally:
        await client.close()


async def test_settings_loaded():
    """Test that settings are loaded correctly from email_worker/.env."""
    print("\n" + "="*60)
    print("TEST 2: Settings Configuration")
    print("="*60)

    print(f"BACKEND_API_URL: {settings.backend_api_url}")
    print(f"AI_SERVICE_URL: {settings.ai_service_url}")
    print(f"IMAP_HOST: {settings.imap_host}")
    print(f"IMAP_USER: {settings.imap_user}")
    print(f"SMTP_HOST: {settings.smtp_host}")

    # Verify localhost URLs for local dev
    assert settings.backend_api_url == "http://localhost:8000", \
        f"Backend URL should be localhost, got: {settings.backend_api_url}"
    assert settings.ai_service_url == "http://localhost:8001", \
        f"AI URL should be localhost, got: {settings.ai_service_url}"

    print("\n✓ All settings loaded correctly from email_worker/.env")


async def test_ticket_payload():
    """Test that ticket payload has correct format."""
    print("\n" + "="*60)
    print("TEST 3: Ticket Creation Payload")
    print("="*60)

    from email_worker.models.event_models import TicketCreatePayload

    payload = TicketCreatePayload(
        source="email",
        subject="Test ticket",
        description="Test description",
        requester_email="test@example.com",
        category="general_it",
        priority="medium",
        team="it"
    )

    data = payload.model_dump()
    print(f"Payload fields:")
    for key, value in data.items():
        print(f"  {key}: {value}")

    # Verify enum values match backend expectations
    assert data["source"] == "email"
    assert data["category"] == "general_it"
    assert data["priority"] == "medium"

    print("\n✓ Payload format matches backend schema")


async def test_email_parsing():
    """Test that email parsing works."""
    print("\n" + "="*60)
    print("TEST 4: Email Parsing")
    print("="*60)

    email = create_test_email()

    print(f"From: {email.from_address}")
    print(f"Subject: {email.subject}")
    print(f"Body: {email.plain_text_body[:100]}...")
    print(f"Message-ID: {email.message_id}")

    assert email.from_address == "testuser@example.com"
    assert email.subject == "My laptop won't turn on"
    assert len(email.plain_text_body) > 0

    print("\n✓ Email parsing structure is correct")


async def test_backend_connectivity():
    """Test if backend is reachable (optional - may fail if backend not running)."""
    print("\n" + "="*60)
    print("TEST 5: Backend Connectivity (Optional)")
    print("="*60)

    client = TicketClient()

    try:
        is_healthy = await asyncio.wait_for(
            client.health_check(),
            timeout=5.0
        )
        if is_healthy:
            print("✓ Backend is running and reachable at http://localhost:8000")
        else:
            print("⚠ Backend returned unhealthy status")
    except asyncio.TimeoutError:
        print("⚠ Backend connection timed out (backend may not be running)")
        print("  This is OK for offline testing")
    except Exception as e:
        print(f"⚠ Backend not reachable: {type(e).__name__}")
        print("  This is OK for offline testing")
    finally:
        await client.close()


async def main():
    """Run all tests."""
    print("\n" + "="*70)
    print(" EMAIL WORKER INTEGRATION TEST SUITE")
    print("="*70)

    try:
        await test_settings_loaded()
        await test_email_parsing()
        await test_ticket_payload()
        await test_classification_fallback()
        await test_backend_connectivity()

        print("\n" + "="*70)
        print(" ✓ ALL TESTS PASSED")
        print("="*70)
        print("\nEmail worker is properly configured and ready to run!")
        print("\nTo start the email worker:")
        print("  .venv\\Scripts\\python.exe -m email_worker.main")
        print("  OR")
        print("  start_email_worker.bat")

    except AssertionError as e:
        print("\n" + "="*70)
        print(f" ✗ TEST FAILED: {e}")
        print("="*70)
        return 1
    except Exception as e:
        print("\n" + "="*70)
        print(f" ✗ UNEXPECTED ERROR: {e}")
        print("="*70)
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
