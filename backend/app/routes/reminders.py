
from datetime import datetime, timezone

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, status

from app.database import get_database
from app.routes.auth import get_current_user
from app.schemas.reminders import (
    ReminderCreate,
    ReminderResponse
)

# Create reminders router
router = APIRouter(
    prefix="/api/reminders",
    tags=["Reminders"]
)


# Get authenticated user's ID
def get_owner_id(current_user):

    if isinstance(current_user, dict):
        user_id = (
            current_user.get("user_id")
            or current_user.get("sub")
            or current_user.get("_id")
            or current_user.get("id")
        )
    else:
        user_id = (
            getattr(current_user, "user_id", None)
            or getattr(current_user, "sub", None)
            or getattr(current_user, "_id", None)
            or getattr(current_user, "id", None)
        )

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authenticated user ID not found."
        )

    return str(user_id)


# Convert MongoDB reminder to API response
def clean_reminder(reminder):

    return {
        "id": str(reminder["_id"]),
        "title": reminder["title"],
        "due_at": reminder["due_at"],
        "notes": reminder.get("notes"),
        "created_at": reminder["created_at"]
    }


# POST: Create a new reminder
@router.post(
    "/",
    response_model=ReminderResponse,
    status_code=status.HTTP_201_CREATED
)
def create_reminder(
    reminder: ReminderCreate,
    current_user: dict = Depends(get_current_user)
):

    db = get_database()
    user_id = get_owner_id(current_user)

    reminder_data = {
        "user_id": user_id,
        "title": reminder.title,
        "due_at": reminder.due_at,
        "notes": reminder.notes,
        "created_at": datetime.now(timezone.utc)
    }

    result = db["reminders"].insert_one(reminder_data)

    reminder_data["_id"] = result.inserted_id

    return clean_reminder(reminder_data)


# GET: Retrieve logged-in user's reminders
@router.get(
    "/",
    response_model=list[ReminderResponse]
)
def get_reminders(
    current_user: dict = Depends(get_current_user)
):

    db = get_database()
    user_id = get_owner_id(current_user)

    cursor = (
        db["reminders"]
        .find({"user_id": user_id})
        .sort("due_at", 1)
    )

    reminders_list = []

    for reminder in cursor:
        reminders_list.append(clean_reminder(reminder))

    return reminders_list


# DELETE: Delete a reminder
@router.delete("/{reminder_id}")
def delete_reminder(
    reminder_id: str,
    current_user: dict = Depends(get_current_user)
):

    db = get_database()
    user_id = get_owner_id(current_user)

    if not ObjectId.is_valid(reminder_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid reminder ID."
        )

    result = db["reminders"].delete_one({
        "_id": ObjectId(reminder_id),
        "user_id": user_id
    })

    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reminder not found."
        )

    return {
        "message": "Reminder deleted successfully."
    }
