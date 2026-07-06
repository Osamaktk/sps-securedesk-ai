import asyncio
import importlib.util
import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import models  # noqa: F401, E402
from database import Base, get_db  # noqa: E402

EVENTS_FEED_PATH = Path(__file__).resolve().parents[1] / "routes" / "events_feed.py"
events_feed_spec = importlib.util.spec_from_file_location("events_feed_route_under_test", EVENTS_FEED_PATH)
assert events_feed_spec and events_feed_spec.loader
events_feed_module = importlib.util.module_from_spec(events_feed_spec)
events_feed_spec.loader.exec_module(events_feed_module)


def test_email_events_feed_requires_internal_api_key(tmp_path, monkeypatch):
    monkeypatch.setenv("INTERNAL_API_KEY", "test-internal-key")

    db_path = tmp_path / "events-feed.db"
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

    app = FastAPI()
    app.include_router(events_feed_module.router)
    app.dependency_overrides[get_db] = override_get_db

    try:
        with TestClient(app) as client:
            missing_header = client.get("/events/email")
            valid_header = client.get(
                "/events/email",
                headers={"X-Internal-Api-Key": "test-internal-key"},
            )
    finally:
        asyncio.run(engine.dispose())

    assert missing_header.status_code == 401
    assert valid_header.status_code == 200
    assert valid_header.json() == []
