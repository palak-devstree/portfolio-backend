"""Authentication router — JWT login endpoint."""
from fastapi import APIRouter, HTTPException, status

from app.core.auth import create_access_token, create_refresh_token, verify_password
from app.core.config import settings
from app.core.logging import get_logger
from app.schemas.auth import LoginRequest, TokenResponse

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])
logger = get_logger(__name__)


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest) -> TokenResponse:
    """
    Admin login endpoint.
    Returns JWT access token (24h) and refresh token (7d).
    Credentials are validated against ADMIN_USERNAME and ADMIN_PASSWORD env vars.
    """
    # Validate credentials
    if (
        request.username != settings.ADMIN_USERNAME
        or request.password != settings.ADMIN_PASSWORD
    ):
        logger.warning(
            "login_failed",
            username=request.username,
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    token_data = {"sub": request.username, "role": "admin"}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    logger.info("login_success", username=request.username)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )
