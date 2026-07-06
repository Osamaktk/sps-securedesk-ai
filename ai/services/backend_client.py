"""Async HTTP client for calling the backend API from the AI service."""

from __future__ import annotations

from typing import Any, Dict, Optional

import httpx

from ai.config.settings import get_settings
from ai.schemas.chat import ChatEscalationTicketPrefill


class BackendAPIError(Exception):
    """Raised when a backend API call fails."""


class BackendClient:
    """Async HTTP client for interacting with the backend ticket API."""

    def __init__(self, base_url: Optional[str] = None) -> None:
        settings = get_settings()
        self.base_url = (base_url or settings.backend_api_url).rstrip("/")
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=httpx.Timeout(30.0),
            )
        return self._client

    async def close(self) -> None:
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    async def create_ticket(
        self,
        *,
        prefill: ChatEscalationTicketPrefill,
        requester_email: Optional[str],
    ) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "source": prefill.source,
            "subject": prefill.subject,
            "description": prefill.description,
            "category": prefill.category.value,
            "priority": prefill.priority.value,
        }
        if requester_email:
            payload["requester_email"] = requester_email
        client = await self._get_client()
        response = await client.post("/tickets", json=payload)
        response.raise_for_status()
        return response.json()


_backend_client = BackendClient()


def get_backend_client() -> BackendClient:
    return _backend_client