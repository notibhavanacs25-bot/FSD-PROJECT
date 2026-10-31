from pymongo import MongoClient
from pymongo.database import Database

from app.config import settings

_client: MongoClient | None = None


def connect_to_mongodb() -> None:
    global _client

    _client = MongoClient(
        settings.mongodb_uri,
        serverSelectionTimeoutMS=5000
    )

    _client.admin.command("ping")

    print(f"Connected to MongoDB database: {settings.mongodb_db}")


def close_mongodb_connection() -> None:
    global _client

    if _client is not None:
        _client.close()
        _client = None


def get_database() -> Database:
    if _client is None:
        raise RuntimeError("MongoDB is not connected")

    return _client[settings.mongodb_db]


def create_database_indexes() -> None:
    db = get_database()

    # 1. Unique email index for authentication
    db["users"].create_index(
        "email",
        unique=True
    )
    print("User email index created.")

    # 2. Reminder lookup index
    db["reminders"].create_index([
        ("user_id", 1),
        ("due_at", 1)
    ])
    print("Reminder index created.")

    # 3. Scheme search index
    db["schemes"].create_index("name")
    print("Scheme name index created.")