"""Intelligent fact extraction from complex messages.

This module uses LLM (GPT-4o-mini) with structured output to extract discrete,
atomic facts from user messages. Each fact is extracted with:
- Content (the fact itself)
- Type classification (identity, preference, project, etc.)
- Confidence score
- Source span (character indices in original message)

Example:
    Input: "I'm Jack, a developer in SF working on an AI app with Python."

    Output: [
        Fact("Name is Jack", type=IDENTITY, confidence=0.99),
        Fact("Profession is developer", type=PROFESSION, confidence=0.95),
        Fact("Located in San Francisco", type=LOCATION, confidence=0.98),
        Fact("Working on AI app", type=PROJECT, confidence=0.92),
        Fact("Uses Python", type=TECHNICAL, confidence=0.90)
    ]
"""

import json
import re
import time
from typing import List, Optional

from openai import AsyncOpenAI
from pydantic import BaseModel, Field

from experiments.config import get_config
from experiments.memory.types import Fact, FactType, ExtractionResult


# Pydantic models for structured output
class ExtractedFact(BaseModel):
    """Single extracted fact with metadata."""
    content: str = Field(description="The fact itself as a clear, concise statement")
    fact_type: str = Field(description="Category: identity, location, profession, preference, project, technical, timeline, relationship, skill, goal, emotion, experience, or other")
    confidence: float = Field(description="Confidence in extraction (0-1)", ge=0.0, le=1.0)
    source_indices: Optional[List[int]] = Field(
        default=None,
        description="[start, end] character indices in original message"
    )


class FactExtractionResponse(BaseModel):
    """Structured response from LLM fact extraction."""
    facts: List[ExtractedFact] = Field(description="List of extracted facts")
    reasoning: str = Field(description="Brief explanation of extraction process")


class FactExtractor:
    """Extract multiple discrete facts from complex messages using LLM.

    This extractor uses GPT-4o-mini with structured output (JSON mode) to
    parse messages into atomic facts, each with metadata for classification
    and confidence scoring.

    The extractor is designed to:
    - Identify discrete, independent facts
    - Avoid redundancy and triviality
    - Preserve semantic meaning
    - Classify facts by type
    - Track source location in original text

    Example:
        >>> extractor = FactExtractor()
        >>> result = await extractor.extract_facts(
        ...     "I'm launching my startup in Q1 2025. "
        ...     "It's an AI app built with Python."
        ... )
        >>> len(result.facts)
        3  # startup, timeline, tech stack
    """

    # Extraction prompt template
    SYSTEM_PROMPT = """You are an expert at extracting discrete, atomic facts from user messages.

Your task is to identify and extract individual facts that can be stored separately in a knowledge base.

Guidelines:
1. **Discrete Facts**: Extract independent facts that make sense on their own
2. **Atomic**: Each fact should contain ONE piece of information
3. **Non-Redundant**: Don't extract duplicate or highly overlapping facts
4. **Meaningful**: Skip trivial or obvious facts (e.g., "I use words")
5. **Preserve Context**: Include minimal context for clarity (e.g., "Prefers X over Y" not just "Likes X")
6. **Classify Accurately**: Assign the most specific fact type
7. **Source Tracking**: Note where each fact appears in the original text

Fact Types:
- identity: Name, age, gender, role
- location: Geographic information, places
- profession: Job, career, occupation
- preference: Likes, dislikes, habits, styles
- project: Work projects, initiatives
- technical: Tools, technologies, frameworks, languages
- timeline: Dates, deadlines, schedules, goals with timeframes
- relationship: Connections to people, teams, organizations
- skill: Abilities, expertise, competencies
- goal: Objectives, aspirations, targets
- emotion: Feelings, moods, emotional states
- experience: Past events, history, background
- other: Anything that doesn't fit above categories

Examples:

Input: "I'm Jack, a software developer in San Francisco. I'm working on Delight, an AI companion app built with Python and React. My goal is to launch by Q1 2025."

Output:
{
  "facts": [
    {"content": "Name is Jack", "fact_type": "identity", "confidence": 0.99},
    {"content": "Software developer", "fact_type": "profession", "confidence": 0.98},
    {"content": "Based in San Francisco", "fact_type": "location", "confidence": 0.99},
    {"content": "Working on Delight project", "fact_type": "project", "confidence": 0.95},
    {"content": "Delight is an AI companion app", "fact_type": "project", "confidence": 0.97},
    {"content": "Tech stack includes Python", "fact_type": "technical", "confidence": 0.96},
    {"content": "Tech stack includes React", "fact_type": "technical", "confidence": 0.96},
    {"content": "Launch goal: Q1 2025", "fact_type": "timeline", "confidence": 0.95}
  ],
  "reasoning": "Extracted 8 discrete facts covering identity, profession, location, project details, technology stack, and timeline"
}

Now extract facts from the user's message."""

    def __init__(self):
        """Initialize fact extractor."""
        self.config = get_config()

        if not self.config.openai_api_key:
            raise ValueError("OPENAI_API_KEY not set in environment")

        self.client = AsyncOpenAI(api_key=self.config.openai_api_key)
        self.model = self.config.chat_model  # gpt-4o-mini

        # Statistics
        self.total_extractions = 0
        self.total_facts_extracted = 0
        self.total_tokens_used = 0

    async def extract_facts(
        self,
        message: str,
        max_facts: Optional[int] = None,
        min_confidence: float = 0.5
    ) -> ExtractionResult:
        """Extract facts from a message using LLM.

        Args:
            message: User message to extract facts from
            max_facts: Maximum number of facts to extract (None = unlimited)
            min_confidence: Minimum confidence threshold for facts

        Returns:
            ExtractionResult with facts and metadata

        Raises:
            ValueError: If message is empty
            openai.APIError: If API call fails

        Example:
            >>> result = await extractor.extract_facts(
            ...     "I prefer TypeScript over JavaScript. "
            ...     "I work late nights and drink coffee."
            ... )
            >>> len(result.facts)
            3
            >>> result.facts[0].content
            'Prefers TypeScript over JavaScript'
        """
        if not message or not message.strip():
            raise ValueError("Message cannot be empty")

        # Check length
        if len(message) < self.config.min_fact_length:
            # Message too short for meaningful extraction
            return ExtractionResult(
                facts=[],
                original_message=message,
                extraction_time_ms=0,
                model_used=self.model
            )

        start_time = time.time()

        try:
            # Prepare user message
            user_message = f"Extract facts from this message:\n\n{message}"

            # Limit facts if specified
            if max_facts:
                user_message += f"\n\nExtract up to {max_facts} most important facts."
            else:
                max_facts = self.config.max_facts_per_message
                user_message += f"\n\nExtract up to {max_facts} facts."

            # Call OpenAI with structured output
            response = await self.client.beta.chat.completions.parse(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": user_message}
                ],
                response_format=FactExtractionResponse,
                temperature=0.3  # Lower temperature for more consistent extraction
            )

            # Parse response
            extraction = response.choices[0].message.parsed

            # Convert to Fact objects
            facts = []
            for extracted_fact in extraction.facts:
                # Filter by confidence
                if extracted_fact.confidence < min_confidence:
                    continue

                # Map string type to enum
                try:
                    fact_type = FactType(extracted_fact.fact_type.lower())
                except ValueError:
                    fact_type = FactType.OTHER

                # Create source span tuple
                source_span = None
                if extracted_fact.source_indices and len(extracted_fact.source_indices) == 2:
                    source_span = tuple(extracted_fact.source_indices)

                facts.append(Fact(
                    content=extracted_fact.content,
                    fact_type=fact_type,
                    confidence=extracted_fact.confidence,
                    source_span=source_span,
                    metadata={
                        "extraction_reasoning": extraction.reasoning,
                        "original_message": message
                    }
                ))

            # Track statistics
            extraction_time_ms = (time.time() - start_time) * 1000
            self.total_extractions += 1
            self.total_facts_extracted += len(facts)
            self.total_tokens_used += response.usage.total_tokens

            return ExtractionResult(
                facts=facts,
                original_message=message,
                extraction_time_ms=extraction_time_ms,
                model_used=self.model,
                token_usage={
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            )

        except Exception as e:
            print(f"❌ Error extracting facts: {e}")
            raise

    async def extract_and_validate(
        self,
        message: str,
        expected_min_facts: int = 1
    ) -> ExtractionResult:
        """Extract facts with validation.

        This method extracts facts and validates that a minimum number
        of facts were found. Useful for ensuring meaningful extraction.

        Args:
            message: Message to extract from
            expected_min_facts: Minimum facts expected

        Returns:
            ExtractionResult

        Raises:
            ValueError: If fewer facts than expected are extracted
        """
        result = await self.extract_facts(message)

        if len(result.facts) < expected_min_facts:
            raise ValueError(
                f"Expected at least {expected_min_facts} facts, "
                f"but only extracted {len(result.facts)}"
            )

        return result

    def get_facts_by_type(
        self,
        facts: List[Fact],
        fact_type: FactType
    ) -> List[Fact]:
        """Filter facts by type.

        Args:
            facts: List of facts
            fact_type: Type to filter by

        Returns:
            Filtered list of facts

        Example:
            >>> preferences = extractor.get_facts_by_type(
            ...     facts,
            ...     FactType.PREFERENCE
            ... )
        """
        return [f for f in facts if f.fact_type == fact_type]

    def get_high_confidence_facts(
        self,
        facts: List[Fact],
        threshold: float = 0.8
    ) -> List[Fact]:
        """Filter facts by confidence threshold.

        Args:
            facts: List of facts
            threshold: Minimum confidence (0-1)

        Returns:
            Facts with confidence >= threshold
        """
        return [f for f in facts if f.confidence >= threshold]

    def print_extraction_summary(self, result: ExtractionResult):
        """Print formatted extraction summary.

        Args:
            result: Extraction result to summarize
        """
        print("\n" + "=" * 70)
        print("📝 Fact Extraction Summary")
        print("=" * 70)
        print(f"Original Message ({len(result.original_message)} chars):")
        print(f'"{result.original_message}"')
        print()
        print(f"Extracted Facts: {len(result.facts)}")
        print("-" * 70)

        for i, fact in enumerate(result.facts, 1):
            print(f"{i}. [{fact.fact_type.value.upper()}] {fact.content}")
            print(f"   Confidence: {fact.confidence:.2f}")
            if fact.source_span:
                start, end = fact.source_span
                source = result.original_message[start:end]
                print(f"   Source: \"{source}\"")
            print()

        print("-" * 70)
        print(f"Extraction Time: {result.extraction_time_ms:.1f}ms")
        print(f"Model: {result.model_used}")
        print(f"Tokens: {result.token_usage.get('total_tokens', 0)}")
        print("=" * 70 + "\n")

    def get_statistics(self) -> dict:
        """Get extraction statistics.

        Returns:
            Dictionary with usage statistics
        """
        return {
            "total_extractions": self.total_extractions,
            "total_facts_extracted": self.total_facts_extracted,
            "total_tokens_used": self.total_tokens_used,
            "avg_facts_per_extraction": (
                self.total_facts_extracted / self.total_extractions
                if self.total_extractions > 0
                else 0
            )
        }


# Convenience function
async def quick_extract(message: str) -> List[Fact]:
    """Quick fact extraction without creating extractor instance.

    Args:
        message: Message to extract facts from

    Returns:
        List of extracted facts

    Example:
        >>> from experiments.memory.fact_extractor import quick_extract
        >>> facts = await quick_extract("I love Python and live in SF")
        >>> len(facts)
        2
    """
    extractor = FactExtractor()
    result = await extractor.extract_facts(message)
    return result.facts


if __name__ == "__main__":
    """Example usage and testing."""
    import asyncio

    async def main():
        extractor = FactExtractor()

        # Test complex message
        message = """
        I'm Jack, a software developer based in San Francisco.
        I'm currently working on Delight, which is an AI companion app
        built with Python, React, and PostgreSQL. My goal is to launch
        by Q1 2025 and raise a seed round. I prefer TypeScript over
        JavaScript and love async programming. I usually work late at
        night and drink lots of coffee. I'm also interested in AI safety
        and have experience with LangChain and OpenAI APIs.
        """

        print("Testing Fact Extraction...")
        print(f"Input message: {len(message)} characters\n")

        result = await extractor.extract_facts(message)

        # Print results
        extractor.print_extraction_summary(result)

        # Filter by type
        print("Facts by Type:")
        for fact_type in FactType:
            type_facts = extractor.get_facts_by_type(result.facts, fact_type)
            if type_facts:
                print(f"\n{fact_type.value.upper()} ({len(type_facts)}):")
                for fact in type_facts:
                    print(f"  - {fact.content} ({fact.confidence:.2f})")

        # High confidence facts
        high_conf = extractor.get_high_confidence_facts(result.facts, threshold=0.9)
        print(f"\n\nHigh Confidence Facts (≥0.9): {len(high_conf)}")
        for fact in high_conf:
            print(f"  - {fact.content} ({fact.confidence:.2f})")

        # Statistics
        stats = extractor.get_statistics()
        print(f"\n\nStatistics:")
        print(f"  Total Extractions: {stats['total_extractions']}")
        print(f"  Total Facts: {stats['total_facts_extracted']}")
        print(f"  Avg Facts/Extraction: {stats['avg_facts_per_extraction']:.1f}")
        print(f"  Total Tokens: {stats['total_tokens_used']}")

    asyncio.run(main())
