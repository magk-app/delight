"""
Comprehensive Memory Cleanup & Analysis

This script performs deep analysis and cleanup of memory database:
1. Question-based memories (queries, not facts)
2. Vague/incomplete statements ("user has a favorite X")
3. Duplicate memories (same or very similar content)
4. Trivial/useless memories (too short, no info)
5. Memories without embeddings (can't be semantically searched)
6. Low confidence memories (if confidence metadata exists)

Provides detailed statistics and selective or bulk cleanup.
"""

import asyncio
import re
from uuid import UUID
from typing import List, Dict, Set, Tuple
from collections import defaultdict
from difflib import SequenceMatcher

from sqlalchemy import select, delete as sql_delete, func
from app.db.session import AsyncSessionLocal
from app.models.memory import Memory


class MemoryCleanupAnalyzer:
    """Comprehensive memory analysis and cleanup."""

    def __init__(self, user_id: UUID = None):
        self.user_id = user_id
        self.all_memories: List[Memory] = []

        # Categories of problematic memories
        self.question_memories: List[Memory] = []
        self.vague_memories: List[Memory] = []
        self.duplicate_groups: List[List[Memory]] = []
        self.trivial_memories: List[Memory] = []
        self.no_embedding_memories: List[Memory] = []
        self.low_confidence_memories: List[Memory] = []

    async def load_memories(self):
        """Load all memories from database."""
        async with AsyncSessionLocal() as db:
            query = select(Memory)
            if self.user_id:
                query = query.where(Memory.user_id == self.user_id)

            result = await db.execute(query)
            self.all_memories = result.scalars().all()

        print(f"✅ Loaded {len(self.all_memories)} total memories")

    def identify_questions(self):
        """Identify question-based memories."""
        question_patterns = [
            r'\?$',  # Ends with question mark
            r'^(what|where|when|why|how|who|which)\b',  # Question words
            r'^(do|does|did|can|could|would|should|will|is|are|was|were)\s+(i|you|we|they|he|she)',
            r'(what|where|when|why|how|who|which)\s+(is|are|was|were|do|does|did)',
        ]

        for memory in self.all_memories:
            content_lower = memory.content.lower().strip()

            for pattern in question_patterns:
                if re.search(pattern, content_lower, re.IGNORECASE):
                    self.question_memories.append(memory)
                    break

        print(f"❓ Found {len(self.question_memories)} question memories")

    def identify_vague_statements(self):
        """Identify vague/incomplete statements."""
        vague_patterns = [
            r'^user has a (favorite|preferred|best)',
            r'^user (likes|prefers|enjoys|wants)',
            r'^(has|have) (a|an|the) (favorite|preferred)',
            r'^there (is|are) (a|an|some)',
            r'^user is interested in',
            r'^user (thinks|believes|feels)',
            r'^(i|we|they) (might|may|could) (like|prefer|want)',
            r'^(probably|maybe|perhaps|possibly)',
            r'(something|someone|somewhere)',  # Contains vague terms
        ]

        for memory in self.all_memories:
            content_lower = memory.content.lower().strip()

            # Skip if already identified as question
            if memory in self.question_memories:
                continue

            # Check for vague patterns
            for pattern in vague_patterns:
                if re.search(pattern, content_lower, re.IGNORECASE):
                    self.vague_memories.append(memory)
                    break

            # Also check for very generic statements
            generic_words = ['has', 'is', 'are', 'might', 'could', 'maybe']
            word_count = len(content_lower.split())
            generic_count = sum(1 for word in generic_words if word in content_lower)

            # If >40% generic words and short, it's vague
            if word_count < 10 and word_count > 0 and (generic_count / word_count) > 0.4:
                if memory not in self.vague_memories:
                    self.vague_memories.append(memory)

        print(f"💭 Found {len(self.vague_memories)} vague memories")

    def identify_duplicates(self, similarity_threshold: float = 0.85):
        """Identify duplicate or near-duplicate memories."""
        processed_ids: Set[UUID] = set()

        for i, mem1 in enumerate(self.all_memories):
            if mem1.id in processed_ids:
                continue

            duplicates = [mem1]

            for mem2 in self.all_memories[i+1:]:
                if mem2.id in processed_ids:
                    continue

                # Calculate text similarity
                similarity = self._text_similarity(mem1.content, mem2.content)

                if similarity >= similarity_threshold:
                    duplicates.append(mem2)
                    processed_ids.add(mem2.id)

            if len(duplicates) > 1:
                self.duplicate_groups.append(duplicates)
                processed_ids.add(mem1.id)

        total_duplicates = sum(len(group) - 1 for group in self.duplicate_groups)
        print(f"🔄 Found {len(self.duplicate_groups)} duplicate groups ({total_duplicates} duplicates)")

    def identify_trivial_memories(self):
        """Identify trivial/useless memories."""
        for memory in self.all_memories:
            content = memory.content.strip()

            # Skip if already categorized
            if (memory in self.question_memories or
                memory in self.vague_memories):
                continue

            # Too short (less than 10 characters)
            if len(content) < 10:
                self.trivial_memories.append(memory)
                continue

            # Contains only common words
            common_words = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'has', 'have', 'had'}
            words = set(content.lower().split())
            if len(words - common_words) < 2:
                self.trivial_memories.append(memory)
                continue

            # Single word memories
            if len(content.split()) == 1:
                self.trivial_memories.append(memory)

        print(f"🗑️  Found {len(self.trivial_memories)} trivial memories")

    def identify_no_embeddings(self):
        """Identify memories without embeddings."""
        for memory in self.all_memories:
            if memory.embedding is None or len(memory.embedding) == 0:
                self.no_embedding_memories.append(memory)

        print(f"📊 Found {len(self.no_embedding_memories)} memories without embeddings")

    def identify_low_confidence(self, threshold: float = 0.5):
        """Identify low confidence memories."""
        for memory in self.all_memories:
            if memory.extra_data and 'confidence' in memory.extra_data:
                confidence = memory.extra_data['confidence']
                if confidence < threshold:
                    # Skip if already categorized as bad
                    if (memory not in self.question_memories and
                        memory not in self.vague_memories and
                        memory not in self.trivial_memories):
                        self.low_confidence_memories.append(memory)

        print(f"⚠️  Found {len(self.low_confidence_memories)} low confidence memories")

    def _text_similarity(self, text1: str, text2: str) -> float:
        """Calculate text similarity using SequenceMatcher."""
        return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()

    def print_analysis_report(self):
        """Print comprehensive analysis report."""
        print("\n" + "=" * 80)
        print("COMPREHENSIVE MEMORY ANALYSIS REPORT")
        print("=" * 80)
        print(f"\n📊 Total Memories: {len(self.all_memories)}")
        print(f"👤 User ID: {self.user_id or 'All users'}")
        print("\n" + "-" * 80)

        # Questions
        if self.question_memories:
            print(f"\n❓ QUESTIONS ({len(self.question_memories)} memories)")
            print("-" * 80)
            for i, mem in enumerate(self.question_memories[:10], 1):
                print(f"{i}. {mem.content[:80]}")
            if len(self.question_memories) > 10:
                print(f"... and {len(self.question_memories) - 10} more")

        # Vague statements
        if self.vague_memories:
            print(f"\n💭 VAGUE STATEMENTS ({len(self.vague_memories)} memories)")
            print("-" * 80)
            for i, mem in enumerate(self.vague_memories[:10], 1):
                print(f"{i}. {mem.content[:80]}")
            if len(self.vague_memories) > 10:
                print(f"... and {len(self.vague_memories) - 10} more")

        # Duplicates
        if self.duplicate_groups:
            print(f"\n🔄 DUPLICATES ({len(self.duplicate_groups)} groups)")
            print("-" * 80)
            for i, group in enumerate(self.duplicate_groups[:5], 1):
                print(f"\nGroup {i} ({len(group)} duplicates):")
                for mem in group[:3]:
                    print(f"  - {mem.content[:70]}")
                if len(group) > 3:
                    print(f"  ... and {len(group) - 3} more")
            if len(self.duplicate_groups) > 5:
                print(f"\n... and {len(self.duplicate_groups) - 5} more groups")

        # Trivial
        if self.trivial_memories:
            print(f"\n🗑️  TRIVIAL ({len(self.trivial_memories)} memories)")
            print("-" * 80)
            for i, mem in enumerate(self.trivial_memories[:10], 1):
                print(f"{i}. {mem.content[:80]}")
            if len(self.trivial_memories) > 10:
                print(f"... and {len(self.trivial_memories) - 10} more")

        # No embeddings
        if self.no_embedding_memories:
            print(f"\n📊 NO EMBEDDINGS ({len(self.no_embedding_memories)} memories)")
            print("-" * 80)
            for i, mem in enumerate(self.no_embedding_memories[:10], 1):
                print(f"{i}. {mem.content[:80]}")
            if len(self.no_embedding_memories) > 10:
                print(f"... and {len(self.no_embedding_memories) - 10} more")

        # Low confidence
        if self.low_confidence_memories:
            print(f"\n⚠️  LOW CONFIDENCE ({len(self.low_confidence_memories)} memories)")
            print("-" * 80)
            for i, mem in enumerate(self.low_confidence_memories[:10], 1):
                conf = mem.extra_data.get('confidence', 0) if mem.extra_data else 0
                print(f"{i}. [{conf:.2f}] {mem.content[:70]}")
            if len(self.low_confidence_memories) > 10:
                print(f"... and {len(self.low_confidence_memories) - 10} more")

        # Summary
        print("\n" + "=" * 80)
        print("CLEANUP RECOMMENDATIONS")
        print("=" * 80)

        total_problematic = (
            len(self.question_memories) +
            len(self.vague_memories) +
            sum(len(group) - 1 for group in self.duplicate_groups) +
            len(self.trivial_memories)
        )

        clean_memories = len(self.all_memories) - total_problematic

        print(f"\n✅ Clean memories: {clean_memories}")
        print(f"❌ Problematic memories: {total_problematic}")
        print(f"📊 Embeddings missing: {len(self.no_embedding_memories)}")
        print(f"⚠️  Low confidence: {len(self.low_confidence_memories)}")
        print(f"\n💾 Database reduction: {total_problematic} → {clean_memories} ({(total_problematic/len(self.all_memories)*100):.1f}% reduction)")
        print("\n" + "=" * 80)

    async def cleanup(self,
                     delete_questions: bool = True,
                     delete_vague: bool = True,
                     delete_duplicates: bool = True,
                     delete_trivial: bool = True,
                     dry_run: bool = True):
        """Perform cleanup based on analysis."""

        to_delete: Set[UUID] = set()

        if delete_questions:
            to_delete.update(mem.id for mem in self.question_memories)

        if delete_vague:
            to_delete.update(mem.id for mem in self.vague_memories)

        if delete_duplicates:
            # Keep first in each group, delete rest
            for group in self.duplicate_groups:
                to_delete.update(mem.id for mem in group[1:])

        if delete_trivial:
            to_delete.update(mem.id for mem in self.trivial_memories)

        if not to_delete:
            print("\n✅ No memories to delete!")
            return

        print(f"\n{'🔍 DRY RUN' if dry_run else '⚠️  LIVE DELETION'}")
        print("=" * 80)
        print(f"Memories to delete: {len(to_delete)}")
        print(f"  - Questions: {len([m for m in self.question_memories if m.id in to_delete])}")
        print(f"  - Vague: {len([m for m in self.vague_memories if m.id in to_delete])}")
        print(f"  - Duplicates: {sum(len(group) - 1 for group in self.duplicate_groups)}")
        print(f"  - Trivial: {len([m for m in self.trivial_memories if m.id in to_delete])}")

        if dry_run:
            print("\n💡 Set dry_run=False to perform actual deletion")
            return

        # Perform deletion
        print("\n🗑️  Deleting memories...")
        async with AsyncSessionLocal() as db:
            deleted_count = 0
            batch_size = 50

            to_delete_list = list(to_delete)

            for i in range(0, len(to_delete_list), batch_size):
                batch = to_delete_list[i:i+batch_size]

                try:
                    stmt = sql_delete(Memory).where(Memory.id.in_(batch))
                    await db.execute(stmt)
                    deleted_count += len(batch)

                    print(f"   Deleted {deleted_count}/{len(to_delete_list)}...")

                except Exception as e:
                    print(f"   ❌ Error deleting batch: {e}")
                    await db.rollback()
                    raise

            await db.commit()
            print(f"\n✅ Successfully deleted {deleted_count} memories")


async def main():
    """Run comprehensive analysis and cleanup."""

    # User ID from your example
    user_id = UUID('385056dd-0f39-4b3b-bf69-04c3724103be')

    print("=" * 80)
    print("COMPREHENSIVE MEMORY CLEANUP")
    print("=" * 80)

    # Initialize analyzer
    analyzer = MemoryCleanupAnalyzer(user_id=user_id)

    # Load memories
    print("\n📂 Loading memories from database...")
    await analyzer.load_memories()

    # Run all analyses
    print("\n🔍 Running comprehensive analysis...\n")
    analyzer.identify_questions()
    analyzer.identify_vague_statements()
    analyzer.identify_duplicates(similarity_threshold=0.85)
    analyzer.identify_trivial_memories()
    analyzer.identify_no_embeddings()
    analyzer.identify_low_confidence(threshold=0.5)

    # Print report
    analyzer.print_analysis_report()

    # Cleanup - SET DRY_RUN TO FALSE TO ACTUALLY DELETE
    print("\n\n")
    await analyzer.cleanup(
        delete_questions=True,
        delete_vague=True,
        delete_duplicates=True,
        delete_trivial=True,
        dry_run=False  # User wants to actually clean up
    )


if __name__ == "__main__":
    asyncio.run(main())
