"""Tests for the message store module."""

import json
import pytest
from email_worker.storage.message_store import MessageStore


class TestMessageStore:
    """Tests for MessageStore JSON-backed mapping."""

    def test_save_and_lookup(self, temp_store):
        temp_store.save_message_mapping("<msg1@ex.com>", "SPS-2026-001")
        assert temp_store.lookup_message_id("<msg1@ex.com>") == "SPS-2026-001"

    def test_lookup_returns_none_when_missing(self, temp_store):
        assert temp_store.lookup_message_id("<nonexistent@ex.com>") is None

    def test_count_starts_at_zero(self, temp_store):
        assert temp_store.count == 0

    def test_count_increments(self, temp_store):
        temp_store.save_message_mapping("<m1@ex.com>", "SPS-1")
        temp_store.save_message_mapping("<m2@ex.com>", "SPS-2")
        assert temp_store.count == 2

    def test_persists_to_disk(self, temp_store):
        temp_store.save_message_mapping("<m3@ex.com>", "SPS-3")
        with open(temp_store._file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert data["<m3@ex.com>"] == "SPS-3"

    def test_loads_from_disk(self, temp_store):
        temp_store.save_message_mapping("<m4@ex.com>", "SPS-4")
        new_store = MessageStore(file_path=temp_store._file_path)
        assert new_store.lookup_message_id("<m4@ex.com>") == "SPS-4"

    def test_delete_mapping(self, temp_store):
        temp_store.save_message_mapping("<m5@ex.com>", "SPS-5")
        temp_store.delete_mapping("<m5@ex.com>")
        assert temp_store.lookup_message_id("<m5@ex.com>") is None
        assert temp_store.count == 0

    def test_skips_empty_message_id(self, temp_store):
        temp_store.save_message_mapping("", "SPS-6")
        assert temp_store.count == 0

    def test_skips_empty_ticket_id(self, temp_store):
        temp_store.save_message_mapping("<m7@ex.com>", "")
        assert temp_store.count == 0