"""
Clerk webhook endpoints for user lifecycle events.
"""

import logging
import uuid
from typing import Annotated, Dict

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from svix.webhooks import Webhook, WebhookVerificationError

from app.core.config import settings
from app.db.session import get_db
from app.schemas.webhook import ClerkWebhookPayload
from app.services.clerk_service import ClerkService

router = APIRouter(prefix="/webhooks", tags=["webhooks"])
logger = logging.getLogger(__name__)


@router.post("/clerk")
async def clerk_webhook_handler(
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Dict[str, str]:
    """
    Handle Clerk user lifecycle webhooks.
    Validates webhook signature and syncs user data to database.

    Events handled:
    - user.created: Create new user in database
    - user.updated: Update existing user in database

    Returns:
        dict: Success status

    Raises:
        HTTPException: 400 for invalid signature or payload
        HTTPException: 500 for processing errors
    """
    # Get Svix webhook headers for signature verification
    svix_id = request.headers.get("svix-id")
    svix_timestamp = request.headers.get("svix-timestamp")
    svix_signature = request.headers.get("svix-signature")

    if not all([svix_id, svix_timestamp, svix_signature]):
        logger.error("Missing required Svix headers")
        raise HTTPException(status_code=400, detail="Missing webhook headers")

    # Get raw body for signature verification
    body = await request.body()

    # Verify webhook signature using Svix
    wh = Webhook(settings.CLERK_WEBHOOK_SECRET)
    try:
        payload = wh.verify(
            body,
            {
                "svix-id": svix_id,
                "svix-timestamp": svix_timestamp,
                "svix-signature": svix_signature,
            },
        )
    except WebhookVerificationError as e:
        logger.error(f"Webhook verification failed: {e}")
        raise HTTPException(status_code=400, detail="Invalid webhook signature")

    # Parse and validate payload
    try:
        webhook_data = ClerkWebhookPayload.model_validate(payload)
    except Exception as e:
        logger.error(f"Invalid webhook payload: {e}")
        raise HTTPException(status_code=400, detail="Invalid payload format")

    # Handle event
    try:
        if webhook_data.type in ["user.created", "user.updated"]:
            user = await ClerkService.create_or_update_user(db, webhook_data.data)
            logger.info(
                f"User synced: {user.clerk_user_id} ({webhook_data.type})",
                extra={
                    "clerk_user_id": user.clerk_user_id,
                    "event_type": webhook_data.type,
                    "user_id": str(user.id),
                },
            )
        elif webhook_data.type == "user.deleted":
            # TODO: Handle user deletion in future story
            logger.info(
                f"User deletion event received (not yet implemented): {webhook_data.data.id}"
            )
        else:
            logger.warning(f"Unhandled event type: {webhook_data.type}")

    except Exception as e:
        logger.error(f"Error processing webhook: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

    return {"status": "success"}
