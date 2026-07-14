"""SMTP outbound email sender with HTML templates, retry logic, and Message-ID tracking."""

from __future__ import annotations

import asyncio
import email.mime.multipart
import email.mime.text
import os
import smtplib
import uuid
from datetime import datetime, timezone
from email.utils import formataddr, formatdate
from typing import Optional

import httpx
from jinja2 import Environment, FileSystemLoader

from email_worker.config.settings import settings
from email_worker.models.email_models import EmailTemplateData
from email_worker.storage.message_store import message_store
from email_worker.utils.logger import logger
from email_worker.utils.retry import async_retry


class EmailSender:
    """Outbound email sender with template rendering and SMTP delivery."""

    def __init__(self) -> None:
        template_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "templates"
        )
        if os.path.isdir(template_dir):
            self._template_env = Environment(
                loader=FileSystemLoader(searchpath=template_dir),
                autoescape=True,
            )
        else:
            self._template_env = Environment(autoescape=True)

    def _generate_message_id(self, ticket_id: Optional[str] = None) -> str:
        """Generate a unique Message-ID for outbound emails."""
        unique = uuid.uuid4().hex[:12]
        domain = settings.email_from_address.split("@")[-1]
        if ticket_id:
            return f"<{ticket_id}.{unique}@{domain}>"
        return f"<{unique}.{datetime.now(timezone.utc).timestamp()}@{domain}>"

    def _build_message(
        self,
        to_email: str,
        subject: str,
        html_body: str,
        plain_text_body: str,
        message_id: Optional[str] = None,
        in_reply_to: Optional[str] = None,
    ):
        """Build a MIME multipart email message with HTML and plain text alternatives."""
        msg = email.mime.multipart.MIMEMultipart("alternative")
        msg["From"] = formataddr(
            (settings.email_from_name, settings.email_from_address)
        )
        msg["To"] = to_email
        msg["Subject"] = subject
        msg["Date"] = formatdate(localtime=True)

        mid = message_id or self._generate_message_id()
        msg["Message-ID"] = mid

        if in_reply_to:
            msg["In-Reply-To"] = in_reply_to

        part_text = email.mime.text.MIMEText(plain_text_body, "plain", "utf-8")
        part_html = email.mime.text.MIMEText(html_body, "html", "utf-8")
        msg.attach(part_text)
        msg.attach(part_html)

        return msg, mid

    def _render_template(self, template_name: str, data: EmailTemplateData) -> str:
        """Render a Jinja2 email template with the given data."""
        try:
            template = self._template_env.get_template(template_name)
            return template.render(**data.model_dump())
        except Exception:
            return f"<h1>{data.ticket_id}</h1><p>{data.subject}</p>"

    @async_retry(max_attempts=3, base_delay=2.0, max_delay=15.0)
    async def _send_via_brevo(
        self, msg: email.mime.multipart.MIMEMultipart, to_email: str
    ) -> None:
        """Send an email via Brevo HTTPS API (bypasses SMTP port restrictions)."""
        # Extract text/html and text/plain parts from the MIMEMultipart message
        html_body = ""
        text_body = ""
        for part in msg.walk():
            if part.get_content_type() == "text/html":
                html_body = part.get_payload(decode=True).decode("utf-8", errors="replace")
            elif part.get_content_type() == "text/plain":
                text_body = part.get_payload(decode=True).decode("utf-8", errors="replace")

        payload = {
            "sender": {
                "name": settings.email_from_name,
                "email": settings.email_from_address,
            },
            "to": [{"email": to_email}],
            "subject": msg["Subject"],
            "htmlContent": html_body or "",
            "textContent": text_body or "",
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://api.brevo.com/v3/smtp/email",
                headers={
                    "api-key": settings.brevo_api_key,
                    "Content-Type": "application/json",
                },
                json=payload,
            )
            response.raise_for_status()
            logger.info(
                "Email sent via Brevo to %s: subject=%s",
                to_email,
                msg["Subject"],
            )

    @async_retry(max_attempts=3, base_delay=2.0, max_delay=15.0)
    async def _send_via_resend(
        self, msg: email.mime.multipart.MIMEMultipart, to_email: str
    ) -> None:
        """Send an email via Resend HTTPS API (bypasses SMTP port restrictions)."""
        # Extract text/html and text/plain parts from the MIMEMultipart message
        html_body = ""
        text_body = ""
        for part in msg.walk():
            if part.get_content_type() == "text/html":
                html_body = part.get_payload(decode=True).decode("utf-8", errors="replace")
            elif part.get_content_type() == "text/plain":
                text_body = part.get_payload(decode=True).decode("utf-8", errors="replace")

        payload = {
            "from": f"{settings.email_from_name} <{settings.email_from_address}>",
            "to": [to_email],
            "subject": msg["Subject"],
            "html": html_body,
            "text": text_body,
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://api.resend.com/emails",
                headers={
                    "Authorization": f"Bearer {settings.resend_api_key}",
                },
                json=payload,
            )
            response.raise_for_status()
            logger.info(
                "Email sent via Resend to %s: subject=%s",
                to_email,
                msg["Subject"],
            )

    @async_retry(max_attempts=3, base_delay=2.0, max_delay=15.0)
    async def _send_smtp(
        self, msg: email.mime.multipart.MIMEMultipart, to_email: str
    ) -> None:
        """Send an email via SMTP with retry logic."""
        loop = asyncio.get_running_loop()

        def _send() -> None:
            with smtplib.SMTP(
                host=settings.smtp_host,
                port=settings.smtp_port,
                timeout=30,
            ) as server:
                if settings.smtp_port != 1025:
                    server.starttls()
                if settings.smtp_user and settings.smtp_password:
                    server.login(settings.smtp_user, settings.smtp_password)
                server.send_message(msg)
                logger.info(
                    "Email sent to %s: subject=%s",
                    to_email,
                    msg["Subject"],
                )

        await loop.run_in_executor(None, _send)

    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_body: str,
        plain_text_body: str,
        ticket_id: Optional[str] = None,
        in_reply_to: Optional[str] = None,
    ) -> str:
        """Build and send an email, storing its Message-ID for thread tracking."""
        message_id = self._generate_message_id(ticket_id)

        msg, mid = self._build_message(
            to_email=to_email,
            subject=subject,
            html_body=html_body,
            plain_text_body=plain_text_body,
            message_id=message_id,
            in_reply_to=in_reply_to,
        )

        if settings.brevo_api_key:
            await self._send_via_brevo(msg, to_email)
        elif settings.resend_api_key:
            await self._send_via_resend(msg, to_email)
        else:
            await self._send_smtp(msg, to_email)

        if ticket_id:
            message_store.save_message_mapping(mid, ticket_id)

        return mid

    async def send_ack_email(
        self,
        to_email: str,
        ticket_id: str,
        subject: str,
        requester_name: str = "",
        guest_token: str = "",
    ) -> str:
        """Send a ticket acknowledgment email."""
        data = EmailTemplateData(
            ticket_id=ticket_id,
            subject=subject,
            requester_name=requester_name or to_email,
            requester_email=to_email,
            description=subject,
            portal_url=settings.portal_url,
            guest_token=guest_token,
        )

        email_subject = f"[{ticket_id}] Your request has been received"
        html_body = self._render_template("ack.html", data)
        plain_text_body = (
            f"Dear {data.requester_name},\n\n"
            f"Your request has been received and assigned ticket {ticket_id}.\n\n"
            f"Subject: {subject}\n\n"
            f"Track your ticket: {settings.portal_url}/tickets/{ticket_id}\n\n"
            f"Thank you,\n{settings.email_from_name}"
        )

        return await self.send_email(
            to_email=to_email,
            subject=email_subject,
            html_body=html_body,
            plain_text_body=plain_text_body,
            ticket_id=ticket_id,
        )

    async def send_agent_reply_email(
        self,
        to_email: str,
        ticket_id: str,
        original_subject: str,
        agent_name: str,
        reply_content: str,
        requester_name: str = "",
    ) -> str:
        """Send an agent reply notification email."""
        data = EmailTemplateData(
            ticket_id=ticket_id,
            subject=original_subject,
            requester_name=requester_name or to_email,
            requester_email=to_email,
            agent_name=agent_name,
            reply_content=reply_content,
            portal_url=settings.portal_url,
        )

        email_subject = f"[{ticket_id}] Re: {original_subject}"
        html_body = self._render_template("agent_reply.html", data)
        plain_text_body = (
            f"Dear {data.requester_name},\n\n"
            f"Agent {agent_name} has replied to your ticket.\n\n"
            f"---\n{reply_content}\n---\n\n"
            f"View the full conversation: {settings.portal_url}/tickets/{ticket_id}\n\n"
            f"Thank you,\n{settings.email_from_name}"
        )

        return await self.send_email(
            to_email=to_email,
            subject=email_subject,
            html_body=html_body,
            plain_text_body=plain_text_body,
            ticket_id=ticket_id,
        )

    async def send_status_change_email(
        self,
        to_email: str,
        ticket_id: str,
        subject: str,
        new_status: str,
        requester_name: str = "",
    ) -> str:
        """Send a ticket status change notification email."""
        data = EmailTemplateData(
            ticket_id=ticket_id,
            subject=subject,
            requester_name=requester_name or to_email,
            requester_email=to_email,
            status=new_status,
            portal_url=settings.portal_url,
        )

        email_subject = f"[{ticket_id}] Status update: {new_status}"
        html_body = self._render_template("status_change.html", data)
        plain_text_body = (
            f"Dear {data.requester_name},\n\n"
            f"The status of your ticket has been updated.\n\n"
            f"Ticket: {ticket_id}\n"
            f"Subject: {subject}\n"
            f"Status: {new_status}\n\n"
            f"View your ticket: {settings.portal_url}/tickets/{ticket_id}\n\n"
            f"Thank you,\n{settings.email_from_name}"
        )

        return await self.send_email(
            to_email=to_email,
            subject=email_subject,
            html_body=html_body,
            plain_text_body=plain_text_body,
            ticket_id=ticket_id,
        )

    async def send_approval_request_email(
        self,
        to_email: str,
        ticket_id: str,
        subject: str,
        requester_name: str = "",
        approval_url: str = "",
    ) -> str:
        """Send an approval request email for high-risk actions."""
        data = EmailTemplateData(
            ticket_id=ticket_id,
            subject=subject,
            requester_name=requester_name or to_email,
            requester_email=to_email,
            approval_url=approval_url or f"{settings.portal_url}/tickets/{ticket_id}/approve",
            portal_url=settings.portal_url,
        )

        email_subject = f"[ACTION REQUIRED] High-Risk Access Request — {ticket_id}"
        html_body = self._render_template("approval_request.html", data)
        plain_text_body = (
            f"ACTION REQUIRED\n\n"
            f"A high-risk access request requires your approval.\n\n"
            f"Ticket: {ticket_id}\n"
            f"Subject: {subject}\n"
            f"Requester: {requester_name}\n\n"
            f"Review and approve: {data.approval_url}\n\n"
            f"Thank you,\n{settings.email_from_name}"
        )

        return await self.send_email(
            to_email=to_email,
            subject=email_subject,
            html_body=html_body,
            plain_text_body=plain_text_body,
            ticket_id=ticket_id,
        )

    async def send_duplicate_notice_email(
        self,
        to_email: str,
        to_name: str,
        existing_ticket_number: str,
        existing_ticket_status: str,
        existing_ticket_subject: str,
        new_ticket_number: str = "",
    ) -> str:
        """Send a duplicate ticket notice email.

        A new ticket IS created (with status duplicate) and then closed/linked
        to the original. This email tells the requester about both tickets.

        Args:
            to_email: Recipient email address.
            to_name: Recipient display name.
            existing_ticket_number: The original (active) ticket number.
            existing_ticket_status: Current status of the original ticket.
            existing_ticket_subject: Subject of the original ticket.
            new_ticket_number: The newly created duplicate ticket's own number.

        Returns:
            The Message-ID of the sent email.
        """
        data = EmailTemplateData(
            ticket_id=existing_ticket_number,
            subject=existing_ticket_subject,
            requester_name=to_name or to_email,
            requester_email=to_email,
            status=existing_ticket_status,
            new_ticket_number=new_ticket_number,
            portal_url=settings.portal_url,
        )

        email_subject = f"[{existing_ticket_number}] We already have your request"
        html_body = self._render_template("duplicate_notice.html", data)
        plain_text_body = (
            f"Dear {data.requester_name},\n\n"
            f"We received a new request from you with similar content to an "
            f"existing open ticket. A new ticket was created for your submission "
            f"and then automatically closed as a duplicate of your original request.\n\n"
            f"Original (active) Ticket: {existing_ticket_number}\n"
            f"Status: {existing_ticket_status}\n"
            f"Subject: {existing_ticket_subject}\n"
        )
        if new_ticket_number:
            plain_text_body += (
                f"\nNew (duplicate) Ticket: {new_ticket_number}\n"
                f"This duplicate ticket has been closed and linked to the original above.\n"
            )
        plain_text_body += (
            f"\nYou do not need to do anything else. You can track your original "
            f"ticket here: {settings.portal_url}/tickets/{existing_ticket_number}\n\n"
            f"Thank you,\n{settings.email_from_name}"
        )

        return await self.send_email(
            to_email=to_email,
            subject=email_subject,
            html_body=html_body,
            plain_text_body=plain_text_body,
            ticket_id=existing_ticket_number,
        )

    async def send_ticket_locked_email(
        self,
        to_email: str,
        to_name: str,
        ticket_number: str,
        ticket_status: str,
    ) -> str:
        """Send a ticket locked notification email.

        Args:
            to_email: Recipient email address.
            to_name: Recipient display name.
            ticket_number: The ticket number.
            ticket_status: Current status of the ticket.

        Returns:
            The Message-ID of the sent email.
        """
        data = EmailTemplateData(
            ticket_id=ticket_number,
            subject="",
            requester_name=to_name or to_email,
            requester_email=to_email,
            status=ticket_status,
            portal_url=settings.portal_url,
        )

        email_subject = f"[{ticket_number}] This ticket is closed"
        html_body = self._render_template("ticket_locked.html", data)
        plain_text_body = (
            f"Dear {data.requester_name},\n\n"
            f"This ticket is closed and cannot be updated.\n\n"
            f"Ticket: {ticket_number}\n"
            f"Status: {ticket_status}\n\n"
            f"To submit a new request, visit: {settings.portal_url}/new\n\n"
            f"Thank you,\n{settings.email_from_name}"
        )

        return await self.send_email(
            to_email=to_email,
            subject=email_subject,
            html_body=html_body,
            plain_text_body=plain_text_body,
            ticket_id=ticket_number,
        )
