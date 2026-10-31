from datetime import datetime
from pydantic import BaseModel, EmailStr, Field

class SignupRequest(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

class UserPublic(BaseModel):
    id: str
    name: str
    email: EmailStr

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class EligibilityRequest(BaseModel):
    age: int | None = Field(default=None, ge=0, le=120)
    state: str | None = None
    annual_income: float | None = Field(default=None, ge=0)
    student: bool | None = None
    farmer: bool | None = None
    category: str | None = None

class ReminderCreate(BaseModel):
    title: str = Field(min_length=2, max_length=160)
    due_at: datetime
    notes: str | None = Field(default=None, max_length=2000)
