from types import SimpleNamespace

from email_worker.notifications import event_listener


def test_redirect_for_real_delivery_returns_original_when_unconfigured(monkeypatch):
    monkeypatch.setattr(
        event_listener,
        "settings",
        SimpleNamespace(email_test_redirect_base=""),
    )

    assert event_listener._redirect_for_real_delivery("user@example.com") == "user@example.com"


def test_redirect_for_real_delivery_rewrites_recipient(monkeypatch):
    monkeypatch.setattr(
        event_listener,
        "settings",
        SimpleNamespace(email_test_redirect_base="tester@example.net"),
    )

    assert event_listener._redirect_for_real_delivery("requester@acme.org") == "tester+requester@example.net"
