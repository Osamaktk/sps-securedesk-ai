import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class NotificationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    recipient_id: uuid.UUID
    ticket_id: uuid.UUID | None = None
    notification_type: str
    title: str
    message: str | None = None
    is_read: bool
    created_at: datetime


class NotificationList(BaseModel):
    notifications: list[NotificationRead]
    unread_count: int


class MarkReadRequest(BaseModel):
    notification_ids: list[uuid.UUID]