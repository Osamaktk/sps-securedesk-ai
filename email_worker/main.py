"""SPS SecureDesk AI Email Pipeline — Main entry point.

Runs the IMAP poller and backend event listener concurrently.
"""

from __future__ import annotations

import asyncio
import os
import signal
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

# Ensure the project root (parent of email_worker/) is on sys.path
# so that 'from email_worker...' imports work when running
# directly from within the email_worker/ directory.
_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from email_worker.api_client.ticket_client import TicketClient
from email_worker.config.settings import settings
from email_worker.imap.poller import IMAPPoller
from email_worker.notifications.event_listener import EventListener
from email_worker.utils.logger import logger


class _HealthHandler(BaseHTTPRequestHandler):
    """Minimal health-check handler — responds 200 OK to satisfy Render's Web Service port scan."""

    def do_GET(self) -> None:
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"ok")

    def log_message(self, format: str, *args) -> None:
        """Silence default HTTP request logging."""
        pass


def start_health_server() -> None:
    """Start a minimal HTTP health server in a daemon thread.

    Render's Web Service tier requires the process to bind to $PORT.
    This server exists only to satisfy that requirement — the actual
    email worker logic runs in the asyncio event loop below.
    """
    port = int(os.getenv("PORT", "10000"))
    server = ThreadingHTTPServer(("0.0.0.0", port), _HealthHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    logger.info("Health server listening on 0.0.0.0:%d (Render port bind)", port)


async def start_imap_poller() -> None:
    """Initialize and run the IMAP poller."""
    client = TicketClient()
    poller = IMAPPoller(ticket_client=client)

    if not settings.imap_host or not settings.imap_user:
        logger.warning(
            "IMAP credentials not configured. Skipping IMAP poller. "
            "Set IMAP_HOST, IMAP_USER, and IMAP_PASSWORD in .env"
        )
        await asyncio.Event().wait()
        return

    try:
        await poller.start_polling()
    except asyncio.CancelledError:
        logger.info("IMAP poller cancelled")
        await poller.stop()
    except Exception as e:
        logger.critical("IMAP poller failed: %s", e, exc_info=True)
        await poller.stop()
        raise


async def start_event_listener() -> None:
    """Initialize and run the backend event listener."""
    client = TicketClient()
    listener = EventListener(ticket_client=client)

    try:
        await listener.start_listening()
    except asyncio.CancelledError:
        logger.info("Event listener cancelled")
        await listener.stop()
    except Exception as e:
        logger.critical("Event listener failed: %s", e, exc_info=True)
        await listener.stop()
        raise


async def main() -> None:
    """Application entry point. Loads config and runs both services concurrently."""
    logger.info("=" * 60)
    logger.info("SPS SecureDesk AI Email Pipeline - Starting")
    logger.info("IMAP: %s:%d", settings.imap_host or "(not set)", settings.imap_port)
    logger.info(
        "SMTP: %s:%d (Mailhog: %s)",
        settings.smtp_host,
        settings.smtp_port,
        settings.is_mailhog,
    )
    logger.info("API: %s", settings.backend_api_url)
    logger.info("=" * 60)

    # Handle graceful shutdown
    shutdown_event = asyncio.Event()

    def _signal_handler() -> None:
        logger.info("Shutdown signal received...")
        shutdown_event.set()

    loop = asyncio.get_event_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, _signal_handler)
        except (ValueError, NotImplementedError):
            # Windows doesn't support add_signal_handler
            pass

    # Run both services concurrently
    tasks = [
        asyncio.create_task(start_imap_poller()),
        asyncio.create_task(start_event_listener()),
    ]

    try:
        await asyncio.wait(
            tasks,
            return_when=asyncio.FIRST_COMPLETED,
        )
    except asyncio.CancelledError:
        pass

    # Cancel remaining tasks
    for task in tasks:
        if not task.done():
            task.cancel()

    await asyncio.gather(*tasks, return_exceptions=True)
    logger.info("SPS SecureDesk AI Email Pipeline - Shutdown complete")


if __name__ == "__main__":
    start_health_server()
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
        sys.exit(0)
    except Exception as e:
        logger.critical("Fatal error: %s", e, exc_info=True)
        sys.exit(1)