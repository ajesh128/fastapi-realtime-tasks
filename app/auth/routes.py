from email_validator import EmailNotValidError
from fastapi import APIRouter, HTTPException, status, Depends
from datetime import datetime, timedelta, timezone
import logging

from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials
from email_validator import validate_email

from app.auth.schemas import RegisterRequest, TokenResponse, UserResponse
from app.auth.service import AuthService
from app.core.dependencies import get_current_user

router = APIRouter()

@router.post(
    "/register", 
    status_code=status.HTTP_201_CREATED,
    responses={409: {"description": "User already exists"}}
)
async def register_user(payload: RegisterRequest):
    """
    API for registering a new user.

    Args:
        payload (RegisterRequest): Request body containing:
            - email (str): User's email
            - password (str): User's password
            - name (str): User's full name
            - role (str): User's role (e.g., "admin" or "user")

    Raises:
        HTTPException: 409 Conflict if the email already exists.
        HTTPException: 500 Internal Server Error for unexpected server-side errors.

    Returns:
        dict: A success message confirming the user has been created.
            Example:
            {
                "message": "User successfully created"
            }
    """
    try:
        # 1. Check if user exists
        if await AuthService.user_validator(payload.email):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, 
                detail="Email already exists"
            )

        # 2. Prepare data
        now = datetime.now(timezone.utc)
        
        doc = {
            "email": payload.email,
            "password": AuthService.hash_password(payload.password),
            "name": payload.name,
            "role": payload.role,
            "created_at": now,
        }

        # 3. Database Insertion
        await AuthService.user_insertion(doc)

        return {"message": "User successfully created"}

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
    """
    API for user login. Validates user credentials and returns JWT tokens.

    Args:
        form (OAuth2PasswordRequestForm, optional): Form data containing:
            - username (email)
            - password

    Raises:
        HTTPException: 400 Bad Request if the email format is invalid.
        HTTPException: 401 Unauthorized if the user does not exist.
        HTTPException: 401 Unauthorized if the password is incorrect.
        HTTPException: 500 Internal Server Error for any unexpected server-side errors.

    Returns:
        TokenResponse: A response containing:
            - access_token (str): JWT access token
            - refresh_token (str): JWT refresh token
            - expires_in (int): Access token expiry in seconds
    """
    try:
        # Validate email
        try:
            normalized = validate_email(
                form.username,
                check_deliverability=False
            ).normalized
        except EmailNotValidError:
            raise HTTPException(
                status_code=400,
                detail="Invalid email format"
            )

        # Validate user
        user = await AuthService.user_validator(normalized)

        if not user:
            raise HTTPException(
                status_code=401,
                detail="Invalid email or password"
            )

        if not AuthService.verify_password(form.password, user["password"]):
            raise HTTPException(
                status_code=401,
                detail="Invalid email or password"
            )

        # Create tokens
        access = AuthService.create_access_token(
            str(user["_id"]),
            user["email"],
            user["role"]
        )
        refresh = AuthService.create_refresh_token(
            str(user["_id"]),
            user["email"],
            user["role"]
        )

        return TokenResponse(
            access_token=access["token"],
            refresh_token=refresh["token"],
            expires_in=int(timedelta(minutes=10).total_seconds())
        )

    # Let FastAPI handle HTTPExceptions properly
    except HTTPException:
        raise
    except Exception as exc:
        logging.error(f"Error occurred in login API: {exc}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_details(current_user: dict = Depends(get_current_user)):
    """
    API to get currently logged-in user details.

    Args:
        current_user: The current authenticated user (extracted from JWT token)

    Returns:
        UserResponse: The user's details including id, email, name, role, and creation date
        
    Raises:
        HTTPException: 401 Unauthorized if the user is not authenticated
    """
    try:
        # Get user details from database using the user ID from the token
        user_details = await AuthService.get_user_by_id(current_user["sub"])
        
        if not user_details:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Format the response to match UserResponse schema
        user_response = UserResponse(
            id=str(user_details["_id"]),
            email=user_details["email"],
            name=user_details["name"],
            role=user_details["role"],
            created_at=user_details.get("created_at")
        )
        
        return user_response
    
    except HTTPException:
        raise
    except Exception as exc:
        logging.error(f"Error occurred in get_current_user_details: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

