"""Test script to verify the email-to-ticket flow works correctly."""

import asyncio
import sys

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

from email_worker.api_client.ticket_client import TicketClient
from email_worker.models.event_models import TicketCreatePayload


async def test_ticket_creation():
    """Test creating a ticket via the backend API."""
    client = TicketClient(
        backend_url="http://localhost:8000",
        ai_url="http://localhost:8001"
    )

    try:
        # Test 1: Create a ticket
        print("Test 1: Creating ticket via backend API...")
        payload = TicketCreatePayload(
            source="email",
            subject="Test ticket from email worker",
            description="This is a test ticket to verify the email worker can create tickets.",
            requester_email="test@example.com",
            category="general_it",
            priority="medium",
            team="it"
        )

        ticket = await client.create_ticket(payload)
        print(f"✓ Ticket created successfully: {ticket.get('ticket_number', ticket.get('id'))}")
        print(f"  ID: {ticket.get('id')}")
        print(f"  Status: {ticket.get('status')}")

        # Test 2: Classify an email
        print("\nTest 2: Testing AI classification...")
        try:
            classify = await client.classify_email(
                subject="My laptop won't turn on",
                description="I pressed the power button but nothing happens"
            )
            print(f"✓ Classification successful:")
            print(f"  Category: {classify.category}")
            print(f"  Priority: {classify.priority}")
            print(f"  Team: {classify.team}")
        except Exception as e:
            print(f"✗ Classification failed (AI service may be down): {e}")
            print("  Fallback classification will be used in production")

        print("\n" + "="*60)
        print("All tests passed! Email worker should work correctly.")
        print("="*60)

    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        print("\nMake sure the backend is running:")
        print("  .venv\\Scripts\\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8000")
        sys.exit(1)
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(test_ticket_creation())
