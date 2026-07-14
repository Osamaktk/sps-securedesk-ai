"""Tests for the guest dashboard signed token (auth_service)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from services import auth_service  # noqa: E402


def test_guest_token_round_trip(monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "test-secret")
    monkeypatch.setenv("ALGORITHM", "HS256")

    token = auth_service.create_guest_dashboard_token("Requester@Example.COM")
    # sub is normalized (lowercased + stripped)
    assert auth_service.decode_guest_dashboard_token(token) == "requester@example.com"


def test_guest_token_rejects_wrong_purpose(monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "test-secret")
    monkeypatch.setenv("ALGORITHM", "HS256")

    # A password_reset token must NOT be accepted as a guest token.
    reset_token = auth_service.create_password_reset_token("someone@example.com")
    try:
        auth_service.decode_guest_dashboard_token(reset_token)
        assert False, "Expected ValueError for wrong-purpose token"
    except ValueError as exc:
        assert "purpose" in str(exc).lower()


def test_guest_token_rejects_garbage(monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "test-secret")
    monkeypatch.setenv("ALGORITHM", "HS256")
    try:
        auth_service.decode_guest_dashboard_token("not-a-real-token")
        assert False, "Expected ValueError for forged token"
    except ValueError:
        pass