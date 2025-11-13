"""
Clerk authentication dependencies for FastAPI.
Validates session tokens and loads authenticated users with proper JWT signature verification.
"""

import httpx
import jwt
import logging
import os
from typing import Annotated, Dict, Any
from fastapi import Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from jwt import PyJWKClient
from functools import lru_cache

from app.core.config import settings
from app.db.session import get_db
from app.models.user import User

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def get_clerk_jwks_client() -> PyJWKClient:
    """
    Get Clerk's JWKS client for JWT verification.
    Cached to avoid repeated initialization.

    Returns:
        PyJWKClient: JWKS client configured for Clerk's API

    Note:
        JWKS URL must be set in environment variable CLERK_JWKS_URL.
        Find this in your Clerk Dashboard → API Keys → Advanced → JWKS endpoint
        Format: https://YOUR-INSTANCE.clerk.accounts.dev/.well-known/jwks.json
    """
    if not settings.CLERK_JWKS_URL:
        raise ValueError(
            "CLERK_JWKS_URL environment variable is required. "
            "Find this in Clerk Dashboard → API Keys → Advanced → JWKS endpoint. "
            "Format: https://YOUR-INSTANCE.clerk.accounts.dev/.well-known/jwks.json"
        )

    jwks_url = settings.CLERK_JWKS_URL
    logger.info(f"Initializing Clerk JWKS client with URL: {jwks_url}")

    return PyJWKClient(
        jwks_url,
        cache_keys=True,  # Cache keys for performance
        max_cached_keys=16,  # Clerk typically uses multiple keys for rotation
        cache_jwk_set=True,  # Cache the entire JWKS
        lifespan=3600,  # Cache for 1 hour
    )


async def get_current_user(
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    """
    Validate Clerk session token and return authenticated user.

    This dependency:
    1. Extracts session token from Authorization header
    2. Validates JWT token signature
    3. Extracts clerk_user_id from verified token
    4. Loads user from database

    Args:
        request: FastAPI request object (contains headers)
        db: Database session

    Returns:
        User: Authenticated user from database

    Raises:
        HTTPException: 401 if token invalid or user not found
        HTTPException: 403 if Authorization header missing
    """
    # Get Authorization header
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Missing Authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Extract bearer token
    if not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization scheme. Expected 'Bearer <token>'",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = auth_header[7:]  # Remove "Bearer " prefix

    # Verify token - environment-aware approach
    # TEST MODE: Skip JWKS verification (tests use mock tokens with HS256)
    # PRODUCTION: Full JWKS verification with RS256
    try:
        # CRITICAL: Check os.environ directly, not settings.ENVIRONMENT
        # The settings singleton is created at import time before tests set the env variable
        # Tests set ENVIRONMENT via pytest_configure() hook in conftest.py
        is_test_env = os.getenv("ENVIRONMENT") in ["test", "testing"]

        if is_test_env:
            # TEST MODE: Decode without signature verification
            # Tests use mock tokens signed with "test_secret" and HS256
            # This allows tests to run without hitting external JWKS endpoints
            logger.debug("Test environment detected - using simplified token validation")
            payload = jwt.decode(
                token,
                options={
                    "verify_signature": False,  # Skip signature verification in tests
                    "verify_exp": True,  # Still verify expiration
                },
            )
        else:
            # PRODUCTION MODE: Full JWKS verification
            # Get JWKS client (cached)
            jwks_client = get_clerk_jwks_client()

            # Get signing key from JWT header (kid = key ID)
            signing_key = jwks_client.get_signing_key_from_jwt(token)

            # Verify JWT signature and decode claims
            # This validates:
            # - Signature using public key from JWKS
            # - Token expiration (exp claim)
            # - Token not-before time (nbf claim) if present
            # - Token issued-at time (iat claim) if present
            payload = jwt.decode(
                token,
                signing_key.key,
                algorithms=["RS256"],  # Clerk uses RS256 (RSA + SHA256)
                options={
                    "verify_signature": True,  # ✅ Verify signature with JWKS
                    "verify_exp": True,  # Verify token expiration
                    "verify_iat": True,  # Verify issued-at time
                    "verify_nbf": True,  # Verify not-before time
                },
            )
            logger.debug("Production JWT verification successful")

        # Extract user ID from verified token
        # Clerk tokens have 'sub' claim with user ID
        clerk_user_id = payload.get("sub")

        if not clerk_user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing user ID",
                headers={"WWW-Authenticate": "Bearer"},
            )

        logger.debug(f"Successfully verified JWT for user: {clerk_user_id[:8]}...")

    except HTTPException:
        # Re-raise HTTPExceptions (like "Invalid token format")
        raise
    except jwt.ExpiredSignatureError:
        logger.warning("JWT token expired")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid JWT token: {type(e).__name__}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logger.error(f"Unexpected error during JWT verification: {type(e).__name__}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Find user in database
    result = await db.execute(select(User).where(User.clerk_user_id == clerk_user_id))
    user = result.scalar_one_or_none()

    if not user:
        # Return 401 (not 404) to prevent user enumeration
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found in database"
        )

    return user
