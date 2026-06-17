"""Tests for the event listener module."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from email_worker.notifications.event_listener import EventListener
from email_worker.api_client.ticket_client import TicketClient
from email_worker.smtp.sender import EmailSender


class TestEventListener:
    """Tests for EventListener."""

    @pytest.fixture
    def mock_ticket_client(self):
        client = AsyncMock(spec=TicketClient)
        client.fetch_events = AsyncMock(return_value=[])
        client.append_timeline_event = AsyncMock(return_value={})
        return client

    @pytest.fixture
    def mock_email_sender(self):
        sender = AsyncMock(spec=EmailSender)
        sender.send_ack_email = AsyncMock(return_value="<test@sps.com>")
        sender.send_agent_reply_email = AsyncMock(return_value="<test@sps.com>")
        sender.send_status_change_email = AsyncMock(return_value="<test@sps.com>")
        sender.send_approval_request_email = AsyncMock(return_value="<test@sps.com>")
        return sender

    @pytest.fixture
    def listener(self, mock_ticket_client, mock_email_sender):
        return EventListener(
            ticket_client=mock_ticket_client,
            email_sender=mock_email_sender,
        )

    @pytest.mark.asyncio
    async def test_poll_events_returns_zero_when_empty(self, listener):
        count = await listener.poll_events()
        assert count == 0

    @pytest.mark.asyncio
    async def test_poll_events_returns_count(self, listener, mock_ticket_client):
        mock_ticket_client.fetch_events = AsyncMock(
            return_value=[
                {
                    "id": "evt1",
                    "event_type": "ticket_created",
                    "ticket_id": "SPS-2026-001",
                    "data": {
                        "requester_email": "user@test.com",
                        "subject": "Help me",
                    },
                }
            ]
        )
        count = await listener.poll_events()
        assert count == 1

    @pytest.mark.asyncio
    async def test_process_ticket_created_event(
        self, listener, mock_email_sender
    ):
        event = {
            "id": "evt2",
            "event_type": "ticket_created",
            "ticket_id": "SPS-2026-002",
            "data": {
                "requester_email": "user@test.com",
                "requester_name": "Test User",
                "subject": "VPN issue",
            },
        }
        await listener._process_event(event)
        mock_email_sender.send_ack_email.assert_called_once()

    @pytest.mark.asyncio
    async def test_process_agent_reply_event(
        self, listener, mock_email_sender, mock_ticket_client
    ):
        event = {
            "id": "evt3",
            "event_type": "agent_reply",
            "ticket_id": "SPS-2026-003",
            "data": {
                "requester_email": "user@test.com",
                "requester_name": "Test User",
                "subject": "VPN issue",
                "agent_name": "Agent Smith",
                "content": "Your VPN is now active.",
            },
        }
        await listener._process_event(event)
        mock_email_sender.send_agent_reply_email.assert_called_once()
        mock_ticket_client.append_timeline_event.assert_called_once()

    @pytest.mark.asyncio
    async def test_process_status_changed_event(
        self, listener, mock_email_sender
    ):
        event = {
            "id": "evt4",
            "event_type": "status_changed",
            "ticket_id": "SPS-2026-004",
            "data": {
                "requester_email": "user@test.com",
                "requester_name": "Test User",
                "subject": "Password reset",
                "new_status": "resolved",
            },
        }
        await listener._process_event(event)
        mock_email_sender.send_status_change_email.assert_called_once()

    @pytest.mark.asyncio
    async def test_process_approval_required_event(
        self, listener, mock_email_sender
    ):
        event = {
            "id": "evt5",
            "event_type": "approval_required",
            "ticket_id": "SPS-2026-005",
            "data": {
                "requester_email": "user@test.com",
                "requester_name": "Test User",
                "subject": "High-risk access",
                "approver_email": "manager@test.com",
            },
        }
        await listener._process_event(event)
        mock_email_sender.send_approval_request_email.assert_called_once()

    @pytest.mark.asyncio
    async def test_skips_duplicate_events(self, listener, mock_email_sender):
        event = {
            "id": "evt6",
            "event_type": "ticket_created",
            "ticket_id": "SPS-2026-006",
            "data": {
                "requester_email": "user@test.com",
                "subject": "Duplicate test",
            },
        }
        await listener._process_event(event)
        await listener._process_event(event)
        assert mock_email_sender.send_ack_email.call_count == 1
