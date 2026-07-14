"""Reproduction test for the duplicate-ticket notification bug (events_feed.py).

Verifies:
  (a) A NORMAL ticket creation still forwards a TICKET_CREATED / "ticket_created" event.
  (b) A DUPLICATE ticket creation forwards ONLY the DUPLICATE_ATTEMPT / "duplicate_detected"
      event for the new ticket; its TICKET_CREATED event must NOT trigger a generic ack.

Uses the real events_feed.email_events_feed route function against an in-memory sqlite DB.
"""
import asyncio
import importlib.util
import sys
import uuid
from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import models  # noqa: F401, E402
from database import Base, get_db  # noqa: F402
from models.ticket import Ticket, TicketStatus, TicketSource, TicketCategory, TicketPriority, TicketTeam, RiskLevel  # noqa: E402
from models.timeline_event import TimelineEvent, TimelineEventType  # noqa: E402

EVENTS_FEED_PATH = Path(__file__).resolve().parents[1] / "routes" / "events_feed.py"
events_feed_spec = importlib.util.spec_from_file_location("events_feed_route_under_test", EVENTS_FEED_PATH)
assert events_feed_spec and events_feed_spec.loader
events_feed_module = importlib.util.module_from_spec(events_feed_spec)
events_feed_spec.loader.exec_module(events_feed_module)


def _make_ticket(status, number="SPS-2026-001", email="requester@example.com"):
    return Ticket(
        id=uuid.uuid4(),
        ticket_number=number,
        source=TicketSource.PORTAL_FORM,
        requester_email=email,
        subject="Test subject",
        description="Test description",
        category=TicketCategory.GENERAL_IT,
        priority=TicketPriority.MEDIUM,
        risk_level=RiskLevel.STANDARD,
        team=TicketTeam.IT,
        status=status,
    )


async def _seed(session: AsyncSession):
    # (a) Normal ticket + TICKET_CREATED event (no User row needed; route
    # falls back to requester_email when ticket.requester is None)
    normal = _make_ticket(TicketStatus.OPEN, number="SPS-2026-N01")
    session.add(normal)
    session.add(TimelineEvent(
        id=uuid.uuid4(),
        ticket_id=normal.id,
        event_type=TimelineEventType.TICKET_CREATED,
        actor_email="requester@example.com",
        is_public=True,
        channel="portal",
    ))

    # (b) Existing original ticket + a DUPLICATE ticket (status=DUPLICATE) with
    #     both a DUPLICATE_ATTEMPT (on the original) and a TICKET_CREATED (on the
    #     duplicate) event — mirroring ticket_service.py's duplicate block.
    original = _make_ticket(TicketStatus.OPEN, number="SPS-2026-ORIG", email="requester@example.com")
    session.add(original)
    dup = _make_ticket(TicketStatus.DUPLICATE, number="SPS-2026-DUP", email="requester@example.com")
    session.add(dup)
    session.add(TimelineEvent(
        id=uuid.uuid4(),
        ticket_id=original.id,
        event_type=TimelineEventType.DUPLICATE_ATTEMPT,
        actor_email="requester@example.com",
        content="Duplicate submission received via portal_form from requester@example.com — created as SPS-2026-DUP",
        is_public=False,
        channel="system",
    ))
    session.add(TimelineEvent(
        id=uuid.uuid4(),
        ticket_id=dup.id,
        event_type=TimelineEventType.TICKET_CREATED,
        actor_email="requester@example.com",
        is_public=True,
        channel="portal",
    ))
    await session.commit()


def test_duplicate_event_feed(tmp_path, monkeypatch):
    monkeypatch.setenv("INTERNAL_API_KEY", "test-internal-key")

    db_path = tmp_path / "dup-feed.db"
    engine = create_async_engine(
        f"sqlite+aiosqlite:///{db_path.as_posix()}",
        connect_args={"check_same_thread": False},
    )
    session_factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    async def create_schema():
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)

    async def override_get_db():
        async with session_factory() as session:
            yield session

    asyncio.run(create_schema())
    asyncio.run(_seed(session_factory()))

    app = FastAPI()
    app.include_router(events_feed_module.router)
    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)

    # Call the real route
    resp = client.get(
        "/events/email",
        headers={"X-Internal-Api-Key": "test-internal-key"},
    )
    assert resp.status_code == 200, resp.text
    events = resp.json()

    types = {e["event_type"] for e in events}
    print("FORWARDED EVENT TYPES:", sorted(types))
    for e in events:
        print("  ", e["event_type"], e["ticket_number"], e.get("data", {}).get("new_ticket_number", ""))

    # (a) Normal ticket creation still produces ticket_created
    assert "ticket_created" in types, "Normal ticket must forward ticket_created ack"

    # (b) Duplicate ticket's TICKET_CREATED must NOT be forwarded
    ticket_created_numbers = [e["ticket_number"] for e in events if e["event_type"] == "ticket_created"]
    assert "SPS-2026-DUP" not in ticket_created_numbers, (
        "Duplicate ticket TICKET_CREATED must NOT be forwarded (no generic ack)"
    )

    # (b) DUPLICATE_ATTEMPT -> duplicate_detected must still be forwarded, with new_ticket_number
    dup_events = [e for e in events if e["event_type"] == "duplicate_detected"]
    assert len(dup_events) == 1, "Exactly one duplicate_detected event expected"
    assert dup_events[0]["data"].get("new_ticket_number") == "SPS-2026-DUP", (
        "duplicate_detected must surface the new duplicate ticket number"
    )

    # Exactly: one ticket_created (normal) + one duplicate_detected
    assert sorted(types) == ["duplicate_detected", "ticket_created"], types
    print("ALL ASSERTIONS PASSED")