"""
User profile API endpoints.
"""

from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.clerk_auth import get_current_user
from app.models.user import User
from app.schemas.user import UserResponse

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: Annotated[User, Depends(get_current_user)],
):
    """
    Get authenticated user's profile.

    This endpoint demonstrates the authentication pattern for protected routes.
    All other protected endpoints should use the same Depends(get_current_user) pattern.

    Returns:
        UserResponse: Authenticated user's profile data

    Raises:
        HTTPException: 401 if token invalid
        HTTPException: 403 if Authorization header missing
    """
    return current_user
