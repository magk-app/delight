"""
Query Preprocessing for Multi-Question Handling

Splits compound queries into individual sub-queries for better memory recall.
Example: "What's my favorite city? And what restaurant do I like?"
→ ["favorite city", "favorite restaurant"]
"""

import re
from typing import List
from openai import AsyncOpenAI
from pydantic import BaseModel, Field

from experiments.config import get_config


class ExtractedQueries(BaseModel):
    """Extracted sub-queries from a compound question."""
    queries: List[str] = Field(description="List of individual search queries extracted from the message")
    reasoning: str = Field(description="Brief explanation of how queries were extracted")


class QueryPreprocessor:
    """Preprocess user queries to extract key concepts and split multi-questions."""

    def __init__(self):
        self.config = get_config()
        self.client = AsyncOpenAI(api_key=self.config.openai_api_key)

    async def extract_search_queries(self, message: str) -> List[str]:
        """
        Extract individual search queries from a potentially compound message.

        Args:
            message: User's message (may contain multiple questions)

        Returns:
            List of individual search queries optimized for memory retrieval

        Example:
            Input: "What's my favorite city? And what restaurant do I like? Also my ethnicity?"
            Output: ["favorite city", "favorite restaurant", "ethnicity"]
        """

        # Quick heuristic: if message is short and has only one question mark, use as-is
        if len(message) < 100 and message.count('?') <= 1 and message.count('.') <= 1:
            return [message]

        # Use LLM to intelligently extract queries
        system_prompt = """You are a query extraction expert for a memory retrieval system.

Your task is to take a user message (which may contain multiple questions or topics) and extract individual search queries that can be used to retrieve relevant memories.

Guidelines:
1. **Extract Key Concepts**: Focus on the core concepts being asked about, not the question words
   - ❌ "what is my favorite city?" → "what is my favorite city"
   - ✅ "what is my favorite city?" → "favorite city"

2. **Split Multiple Questions**: If the message contains multiple distinct questions, extract each one separately
   - Input: "What's my city? What restaurant do I like?"
   - Output: ["favorite city", "favorite restaurant"]

3. **Remove Question Words**: Strip out "what", "where", "when", "how", "do", "does", etc.
   - Keep only the substantive concepts

4. **Preserve Context**: Keep enough context for meaningful search
   - ✅ "favorite restaurant"
   - ✅ "programming language preference"
   - ❌ "restaurant" (too vague)

5. **Merge Related Concepts**: If multiple parts refer to the same concept, merge them
   - Input: "Tell me about my favorite city. What city do I like the most?"
   - Output: ["favorite city"] (not both)

6. **Handle Statements**: If the message is a statement (not question), extract key topics
   - Input: "I want to know about my programming preferences and favorite tools"
   - Output: ["programming preferences", "favorite tools"]

Examples:

Input: "What is my favorite city? And what restaurant do I like? Also what's my ethnicity?"
Output:
{
  "queries": ["favorite city", "favorite restaurant", "ethnicity"],
  "reasoning": "Split into 3 distinct questions, removed question words, extracted core concepts"
}

Input: "Do I like TypeScript or JavaScript better?"
Output:
{
  "queries": ["TypeScript vs JavaScript preference"],
  "reasoning": "Single comparison question, preserved both technologies and preference context"
}

Input: "Tell me about my programming background"
Output:
{
  "queries": ["programming background"],
  "reasoning": "Single topic statement, extracted core concept"
}

Now extract search queries from the user's message."""

        try:
            response = await self.client.beta.chat.completions.parse(
                model=self.config.chat_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Extract search queries from:\n\n{message}"}
                ],
                response_format=ExtractedQueries,
                temperature=0.3
            )

            extracted = response.choices[0].message.parsed

            # Filter out empty queries
            queries = [q.strip() for q in extracted.queries if q.strip()]

            if not queries:
                # Fallback to original message
                return [message]

            print(f"\n🔍 Query Preprocessing:")
            print(f"   Original: {message}")
            print(f"   Extracted: {queries}")
            print(f"   Reasoning: {extracted.reasoning}")

            return queries

        except Exception as e:
            print(f"⚠️  Query preprocessing failed: {e}")
            print(f"   Falling back to original message")
            return [message]

    def simple_split(self, message: str) -> List[str]:
        """
        Simple rule-based query splitting (faster, no LLM call).

        Args:
            message: User message

        Returns:
            List of sub-queries

        Example:
            Input: "What's my city? What's my restaurant?"
            Output: ["my city", "my restaurant"]
        """

        # Split on sentence boundaries
        sentences = re.split(r'[.?!]+', message)

        queries = []
        question_words = r'\b(what|where|when|why|how|who|which|do|does|did|can|could|would|should|is|are|was|were)\b'

        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue

            # Remove question words
            cleaned = re.sub(question_words, '', sentence, flags=re.IGNORECASE).strip()

            # Remove leading articles
            cleaned = re.sub(r'^\b(a|an|the|my|your|our)\b\s*', '', cleaned, flags=re.IGNORECASE).strip()

            if cleaned and len(cleaned) > 3:
                queries.append(cleaned)

        return queries if queries else [message]


async def quick_extract(message: str) -> List[str]:
    """Quick extraction without creating preprocessor instance."""
    preprocessor = QueryPreprocessor()
    return await preprocessor.extract_search_queries(message)


if __name__ == "__main__":
    """Test query preprocessing."""
    import asyncio

    async def test():
        preprocessor = QueryPreprocessor()

        test_messages = [
            "What is my favorite city?",
            "What's my favorite city? And what restaurant do I like? Also what's my ethnicity?",
            "Do I prefer TypeScript or JavaScript?",
            "Tell me about my programming background and favorite tools",
            "What university do I go to right now?",
        ]

        for msg in test_messages:
            print("\n" + "="*80)
            queries = await preprocessor.extract_search_queries(msg)
            print(f"\nResult: {queries}")

    asyncio.run(test())
