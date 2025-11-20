"""
Memory Cleanup API

Provides endpoints for analyzing and cleaning up problematic memories:
- Questions, vague statements, duplicates, trivial memories
- Frontend UI can trigger analysis and cleanup
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict
from uuid import UUID
import re
from difflib import SequenceMatcher

from sqlalchemy import select, delete as sql_delete
from app.db.session import AsyncSessionLocal
from app.models.memory import Memory

router = APIRouter(prefix="/api/cleanup", tags=["cleanup"])


# Pydantic models
class MemoryIssue(BaseModel):
    id: str
    content: str
    issue_type: str  # "question", "vague", "duplicate", "trivial", "no_embedding"
    severity: str  # "high", "medium", "low"
    created_at: str
    memory_type: str


class CleanupAnalysisResponse(BaseModel):
    total_memories: int
    issues_found: int
    breakdown: Dict[str, int]
    issues: List[MemoryIssue]
    recommendations: List[str]


class CleanupRequest(BaseModel):
    user_id: str
    delete_questions: bool = True
    delete_vague: bool = True
    delete_duplicates: bool = True
    delete_trivial: bool = False  # User might want to keep some
    similarity_threshold: float = 0.85


class CleanupResponse(BaseModel):
    deleted_count: int
    breakdown: Dict[str, int]
    remaining_memories: int


# Helper functions
def is_question(content: str) -> bool:
    """Check if content is a question."""
    question_patterns = [
        r'\?$',
        r'^(what|where|when|why|how|who|which)\b',
        r'^(do|does|did|can|could|would|should)\s+(i|you|we)',
    ]
    content_lower = content.lower().strip()
    return any(re.search(p, content_lower, re.IGNORECASE) for p in question_patterns)


def is_vague(content: str) -> bool:
    """Check if content is vague/incomplete."""
    vague_patterns = [
        r'^user has a (favorite|preferred)',
        r'^user (likes|prefers|wants)',
        r'(something|someone|somewhere)',
    ]
    content_lower = content.lower().strip()
    return any(re.search(p, content_lower, re.IGNORECASE) for p in vague_patterns)


def is_trivial(content: str) -> bool:
    """Check if content is trivial."""
    if len(content.strip()) < 10:
        return True
    if len(content.split()) == 1:
        return True
    return False


def text_similarity(text1: str, text2: str) -> float:
    """Calculate text similarity."""
    return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()


@router.post("/analyze", response_model=CleanupAnalysisResponse)
async def analyze_memories(user_id: str):
    """Analyze memories and identify issues."""

    try:
        user_uuid = UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID")

    async with AsyncSessionLocal() as db:
        # Fetch all memories
        stmt = select(Memory).where(Memory.user_id == user_uuid)
        result = await db.execute(stmt)
        memories = result.scalars().all()

        if not memories:
            return CleanupAnalysisResponse(
                total_memories=0,
                issues_found=0,
                breakdown={},
                issues=[],
                recommendations=["No memories found for this user"]
            )

        # Analyze
        issues: List[MemoryIssue] = []
        breakdown = {
            "questions": 0,
            "vague": 0,
            "duplicates": 0,
            "trivial": 0,
            "no_embedding": 0,
        }

        processed_ids = set()

        for i, mem in enumerate(memories):
            # Check for questions
            if is_question(mem.content):
                issues.append(MemoryIssue(
                    id=str(mem.id),
                    content=mem.content,
                    issue_type="question",
                    severity="high",
                    created_at=mem.created_at.isoformat() if mem.created_at else "",
                    memory_type=mem.memory_type.value if hasattr(mem.memory_type, 'value') else str(mem.memory_type)
                ))
                breakdown["questions"] += 1
                processed_ids.add(mem.id)
                continue

            # Check for vague
            if is_vague(mem.content):
                issues.append(MemoryIssue(
                    id=str(mem.id),
                    content=mem.content,
                    issue_type="vague",
                    severity="high",
                    created_at=mem.created_at.isoformat() if mem.created_at else "",
                    memory_type=mem.memory_type.value if hasattr(mem.memory_type, 'value') else str(mem.memory_type)
                ))
                breakdown["vague"] += 1
                processed_ids.add(mem.id)
                continue

            # Check for trivial
            if is_trivial(mem.content):
                issues.append(MemoryIssue(
                    id=str(mem.id),
                    content=mem.content,
                    issue_type="trivial",
                    severity="medium",
                    created_at=mem.created_at.isoformat() if mem.created_at else "",
                    memory_type=mem.memory_type.value if hasattr(mem.memory_type, 'value') else str(mem.memory_type)
                ))
                breakdown["trivial"] += 1
                processed_ids.add(mem.id)
                continue

            # Check for no embedding
            if mem.embedding is None:
                issues.append(MemoryIssue(
                    id=str(mem.id),
                    content=mem.content,
                    issue_type="no_embedding",
                    severity="low",
                    created_at=mem.created_at.isoformat() if mem.created_at else "",
                    memory_type=mem.memory_type.value if hasattr(mem.memory_type, 'value') else str(mem.memory_type)
                ))
                breakdown["no_embedding"] += 1

            # Check for duplicates (compare with remaining memories)
            if mem.id not in processed_ids:
                for mem2 in memories[i+1:]:
                    if mem2.id in processed_ids:
                        continue

                    if text_similarity(mem.content, mem2.content) >= 0.85:
                        # Mark duplicate (keep first, flag second)
                        issues.append(MemoryIssue(
                            id=str(mem2.id),
                            content=mem2.content,
                            issue_type="duplicate",
                            severity="medium",
                            created_at=mem2.created_at.isoformat() if mem2.created_at else "",
                            memory_type=mem2.memory_type.value if hasattr(mem2.memory_type, 'value') else str(mem2.memory_type)
                        ))
                        breakdown["duplicates"] += 1
                        processed_ids.add(mem2.id)

        # Generate recommendations
        recommendations = []
        if breakdown["questions"] > 0:
            recommendations.append(f"Delete {breakdown['questions']} question-based memories (high priority)")
        if breakdown["vague"] > 0:
            recommendations.append(f"Delete {breakdown['vague']} vague statements (high priority)")
        if breakdown["duplicates"] > 0:
            recommendations.append(f"Delete {breakdown['duplicates']} duplicate memories (medium priority)")
        if breakdown["trivial"] > 0:
            recommendations.append(f"Review {breakdown['trivial']} trivial memories (low priority)")
        if breakdown["no_embedding"] > 0:
            recommendations.append(f"{breakdown['no_embedding']} memories missing embeddings - regenerate recommended")

        if not recommendations:
            recommendations.append("✅ All memories are clean!")

        return CleanupAnalysisResponse(
            total_memories=len(memories),
            issues_found=len(issues),
            breakdown=breakdown,
            issues=issues,
            recommendations=recommendations
        )


@router.post("/execute", response_model=CleanupResponse)
async def execute_cleanup(request: CleanupRequest):
    """Execute cleanup based on user selections."""

    try:
        user_uuid = UUID(request.user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID")

    async with AsyncSessionLocal() as db:
        # Fetch all memories
        stmt = select(Memory).where(Memory.user_id == user_uuid)
        result = await db.execute(stmt)
        memories = result.scalars().all()

        to_delete = set()
        breakdown = {
            "questions": 0,
            "vague": 0,
            "duplicates": 0,
            "trivial": 0,
        }

        processed_ids = set()

        for i, mem in enumerate(memories):
            # Questions
            if request.delete_questions and is_question(mem.content):
                to_delete.add(mem.id)
                breakdown["questions"] += 1
                continue

            # Vague
            if request.delete_vague and is_vague(mem.content):
                to_delete.add(mem.id)
                breakdown["vague"] += 1
                continue

            # Trivial
            if request.delete_trivial and is_trivial(mem.content):
                to_delete.add(mem.id)
                breakdown["trivial"] += 1
                continue

            # Duplicates
            if request.delete_duplicates and mem.id not in processed_ids:
                for mem2 in memories[i+1:]:
                    if text_similarity(mem.content, mem2.content) >= request.similarity_threshold:
                        to_delete.add(mem2.id)
                        breakdown["duplicates"] += 1
                        processed_ids.add(mem2.id)

        # Delete in batches
        if to_delete:
            to_delete_list = list(to_delete)
            batch_size = 50

            for i in range(0, len(to_delete_list), batch_size):
                batch = to_delete_list[i:i+batch_size]
                stmt = sql_delete(Memory).where(Memory.id.in_(batch))
                await db.execute(stmt)

            await db.commit()

        # Count remaining
        stmt = select(Memory).where(Memory.user_id == user_uuid)
        result = await db.execute(stmt)
        remaining = len(result.scalars().all())

        return CleanupResponse(
            deleted_count=len(to_delete),
            breakdown=breakdown,
            remaining_memories=remaining
        )


@router.get("/stats")
async def get_cleanup_stats(user_id: str):
    """Get quick stats about memory quality."""

    try:
        user_uuid = UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID")

    async with AsyncSessionLocal() as db:
        stmt = select(Memory).where(Memory.user_id == user_uuid)
        result = await db.execute(stmt)
        memories = result.scalars().all()

        stats = {
            "total": len(memories),
            "questions": sum(1 for m in memories if is_question(m.content)),
            "vague": sum(1 for m in memories if is_vague(m.content)),
            "trivial": sum(1 for m in memories if is_trivial(m.content)),
            "no_embeddings": sum(1 for m in memories if m.embedding is None),
        }

        stats["clean"] = stats["total"] - (stats["questions"] + stats["vague"] + stats["trivial"])
        stats["quality_score"] = (stats["clean"] / stats["total"] * 100) if stats["total"] > 0 else 0

        return stats
