from email_validator import EmailNotValidError
from fastapi import APIRouter, HTTPException, status, Depends
from datetime import datetime, timedelta, timezone
import uuid
import logging

from fastapi.security import OAuth2PasswordRequestForm
from email_validator import validate_email

from app.auth.schemas import RegisterRequest, TokenResponse
from app.auth.service import AuthService

router = APIRouter()

@router.post(
    "/register", 
    status_code=status.HTTP_201_CREATED,
    responses={409: {"description": "User already exists"}}
)
async def register_user(payload: RegisterRequest):
    try:
        # 1. Check if user exists
        if await AuthService.user_validator(payload.email):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, 
                detail="Email already exists"
            )

        # 2. Prepare data
        now = datetime.now(timezone.utc)
        user_id = str(uuid.uuid4())
        
        doc = {
            "user_id": user_id,
            "email": payload.email,
            "password": AuthService.hash_password(payload.password),
            "name": payload.name,
            "role": payload.role,
            "created_at": now,
        }

        # 3. Database Insertion
        await AuthService.user_insertion(doc)

        return {"message": "User successfully created", "user_id": user_id}

    except HTTPException:
        # Re-raise HTTP exceptions so they reach the client
        raise
    except Exception as exc:
        logging.error(f"Critical error in register_user: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal server error occurred"
        )
    

@router.post("/login", response_model=TokenResponse)
async def login(form: OAuth2PasswordRequestForm = Depends()):
    try:
        try:
            normalized = validate_email(form.username, check_deliverability=False).normalized
        except EmailNotValidError:
            raise HTTPException(status_code=400, detail="Invalid email format")
        user = await AuthService.user_validator(normalized)
        if not user or not AuthService.verify_password(form.password, user["password"]):
            raise HTTPException(status_code=401, detail="Invalid email or password")
        access = AuthService.create_access_token(str(user["user_id"]), user["email"], user["role"])
        refresh = AuthService.create_refresh_token(str(user["user_id"]), user["email"], user["role"])
        return TokenResponse(
            access_token=access["token"],
            refresh_token=refresh["token"],
            expires_in=int(timedelta(minutes=10).total_seconds())
        )
    except Exception as exc:
        logging.error(f"error occured in register user function {exc}")
        return []
