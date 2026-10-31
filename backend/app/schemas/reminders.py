
from datetime import datetime, timezone

from pydantic import BaseModel, Field, field_validator


class ReminderCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=150)
    due_at: datetime
    notes: str | None = Field(default=None, max_length=1000)

    @field_validator("due_at")
    @classmethod
    def validate_due_at(cls, value: datetime):
        # A timezone must be provided.
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("Due date must include a timezone.")

        # Reminders must be scheduled in the future.
        if value <= datetime.now(timezone.utc):
            raise ValueError("Due date must be in the future.")

        return value


class ReminderResponse(BaseModel):
    id: str
    title: str
    due_at: datetime
    notes: str | None = None
    created_at: datetime
