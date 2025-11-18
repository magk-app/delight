"""
Agent Preferences API endpoints - Customize AI agent behavior

Enables users to fine-tune:
- Memory retrieval settings (recency bias, similarity thresholds)
- Model selection (which LLM to use for different tasks)
- Reasoning depth (how thorough the agent should be)
- Safety and validation settings
- Interaction style (verbosity, transparency, language)
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.clerk_auth import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.models.user_preferences import AgentPreferences
from app.schemas.agent_preferences import (
    AgentPreferencesCreate,
    AgentPreferencesUpdate,
    AgentPreferencesResponse,
)

router = APIRouter(prefix="/agent-preferences", tags=["agent-preferences"])


@router.get("", response_model=AgentPreferencesResponse)
async def get_agent_preferences(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Get user's agent preferences

    Returns preferences or creates default if none exist.
    """
    result = await db.execute(
        select(AgentPreferences).where(AgentPreferences.user_id == current_user.id)
    )
    prefs = result.scalar_one_or_none()

    if not prefs:
        # Create default preferences
        prefs = AgentPreferences(user_id=current_user.id)
        db.add(prefs)
        await db.commit()
        await db.refresh(prefs)

    return prefs


@router.post("", response_model=AgentPreferencesResponse, status_code=201)
async def create_agent_preferences(
    prefs_data: AgentPreferencesCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Create agent preferences

    Raises:
        409: Preferences already exist (use PUT to update)
    """
    # Check if preferences already exist
    result = await db.execute(
        select(AgentPreferences).where(AgentPreferences.user_id == current_user.id)
    )
    existing = result.scalar_one_or_none()

    if existing:
        raise HTTPException(
            status_code=409,
            detail="Agent preferences already exist. Use PUT /agent-preferences to update.",
        )

    # Create new preferences
    prefs = AgentPreferences(
        user_id=current_user.id,
        **prefs_data.model_dump(),
    )

    db.add(prefs)
    await db.commit()
    await db.refresh(prefs)

    return prefs


@router.put("", response_model=AgentPreferencesResponse)
async def update_agent_preferences(
    prefs_data: AgentPreferencesUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Update agent preferences (partial updates allowed)

    Only updates fields provided in request.

    Raises:
        404: Preferences not found (use POST to create)
    """
    result = await db.execute(
        select(AgentPreferences).where(AgentPreferences.user_id == current_user.id)
    )
    prefs = result.scalar_one_or_none()

    if not prefs:
        raise HTTPException(
            status_code=404,
            detail="Agent preferences not found. Use POST /agent-preferences to create.",
        )

    # Update only provided fields
    update_data = prefs_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(prefs, field, value)

    await db.commit()
    await db.refresh(prefs)

    return prefs


@router.delete("", status_code=204)
async def reset_agent_preferences(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Reset agent preferences to defaults

    Deletes current preferences; default will be created on next GET.
    """
    result = await db.execute(
        select(AgentPreferences).where(AgentPreferences.user_id == current_user.id)
    )
    prefs = result.scalar_one_or_none()

    if prefs:
        await db.delete(prefs)
        await db.commit()

    return None


@router.get("/dict", response_model=dict)
async def get_preferences_as_dict(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Get agent preferences as nested dictionary

    Returns preferences organized by category:
    - memory: retrieval settings
    - models: model selection
    - reasoning: depth and multi-hop settings
    - safety: validation and filtering
    - interaction: style and language

    Useful for displaying settings in UI or passing to agents.
    """
    result = await db.execute(
        select(AgentPreferences).where(AgentPreferences.user_id == current_user.id)
    )
    prefs = result.scalar_one_or_none()

    if not prefs:
        # Create default preferences
        prefs = AgentPreferences(user_id=current_user.id)
        db.add(prefs)
        await db.commit()
        await db.refresh(prefs)

    return prefs.to_dict()
