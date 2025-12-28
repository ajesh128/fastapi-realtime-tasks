from fastapi import Depends, HTTPException, Request, WebSocket, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from app.core.security import JWT_SECRET_KEY, JWT_ALGORITHM
from app.websockets.manager import ConnectionManager


security = HTTPBearer()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """
    Dependency to get current user from JWT token

    Args:
        credentials: Bearer token from Authorization header

    Returns:
        Token payload with user information

    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        token = credentials.credentials
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])

        # Verify it's an access token
        if payload.get("type") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    

async def is_admin_user(current_user: dict = Depends(get_current_user)) -> None:
    """
    Dependency to check if current user is an admin

    Args:
        current_user: Token payload with user information

    Raises:
        HTTPException: If user is not an admin
    """
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    

def get_manager(websocket: WebSocket) -> ConnectionManager:
    return websocket.app.state.manager
