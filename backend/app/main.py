
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import (
    connect_to_mongodb,
    close_mongodb_connection,
    create_database_indexes
)
from app.routes import auth, schemes, reminders


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Connect to MongoDB
    connect_to_mongodb()

    # Create required database indexes
    create_database_indexes()

    yield

    # Close MongoDB connection when application shuts down
    close_mongodb_connection()


app = FastAPI(
    title="NagrikAI API",
    description="Citizen Assistance Platform",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"]
)

# Register API routes
app.include_router(auth.router)
app.include_router(schemes.router)
app.include_router(reminders.router)


@app.get("/")
def home():
    return {
        "message": "Welcome to NagrikAI API"
    }


@app.get("/api/health")
def health():
    return {
        "status": "healthy"
    }
