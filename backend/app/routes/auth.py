from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pymongo.errors import DuplicateKeyError
from jwt.exceptions import InvalidTokenError

from app.database import get_database
from app.schemas.auth import (
    SignupRequest,
    LoginRequest,
    UserResponse,
    TokenResponse
)
from app.services.auth import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token
)


router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"]
)

# Swagger UI will show an Authorize button.
security = HTTPBearer(auto_error=False)


# ------------------------------------------------
# SIGNUP
# POST /api/auth/signup
# ------------------------------------------------

@router.post(
    "/signup",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
def signup(user: SignupRequest):

    db = get_database()
    users = db["users"]

    email = user.email.lower()

    # Check whether the email already exists.
    existing_user = users.find_one({"email": email})

    if existing_user:
        raise HTTPException(
            status_code=409,
            detail="An account with this email already exists."
        )

    # Hash the password.
    hashed_password = hash_password(user.password)

    user_document = {
        "name": user.name.strip(),
        "email": email,
        "password_hash": hashed_password
    }

    try:
        result = users.insert_one(user_document)

    except DuplicateKeyError:
        raise HTTPException(
            status_code=409,
            detail="An account with this email already exists."
        )

    return UserResponse(
        id=str(result.inserted_id),
        name=user_document["name"],
        email=user_document["email"]
    )


# ------------------------------------------------
# LOGIN
# POST /api/auth/login
# ------------------------------------------------

@router.post(
    "/login",
    response_model=TokenResponse
)
def login(user: LoginRequest):

    db = get_database()
    users = db["users"]

    email = user.email.lower()

    # Find the user by email.
    existing_user = users.find_one({"email": email})

    if not existing_user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password."
        )

    # Verify the submitted password.
    password_is_valid = verify_password(
        user.password,
        existing_user["password_hash"]
    )

    if not password_is_valid:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password."
        )

    # Generate JWT token.
    token = create_access_token(
        str(existing_user["_id"])
    )

    return TokenResponse(
        access_token=token,
        token_type="bearer"
    )


# ------------------------------------------------
# GET CURRENT USER FROM JWT
# ------------------------------------------------

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):

    if credentials is None:
        raise HTTPException(
            status_code=401,
            detail="Authentication token is required.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    try:
        payload = decode_access_token(credentials.credentials)

        user_id = payload.get("sub")

        if not user_id:
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication token."
            )

        if not ObjectId.is_valid(user_id):
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication token."
            )

    except InvalidTokenError:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired authentication token.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    db = get_database()

    current_user = db["users"].find_one({
        "_id": ObjectId(user_id)
    })

    if not current_user:
        raise HTTPException(
            status_code=401,
            detail="User account not found."
        )

    return current_user


# ------------------------------------------------
# PROTECTED PROFILE
# GET /api/auth/me
# ------------------------------------------------

@router.get(
    "/me",
    response_model=UserResponse
)
def get_my_profile(
    current_user: dict = Depends(get_current_user)
):

    return UserResponse(
        id=str(current_user["_id"]),
        name=current_user["name"],
        email=current_user["email"]
    )