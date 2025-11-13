"""
Simple Eliza Agent for vertical slice (Story 2.5).

This is a basic streaming agent without LangGraph. Story 2.3 will replace
this with a full LangGraph-based agent with advanced memory retrieval.
"""

import logging
from typing import AsyncIterator, Dict, List

from openai import AsyncOpenAI

from app.models.memory import Memory

logger = logging.getLogger(__name__)


class SimpleElizaAgent:
    """
    Simple Eliza agent without LangGraph (for vertical slice).

    Provides basic streaming responses with memory context. Uses OpenAI
    GPT-4o-mini for cost-effective chat generation.
    """

    def __init__(self, openai_api_key: str):
        """
        Initialize Simple Eliza Agent.

        Args:
            openai_api_key: OpenAI API key for GPT-4o-mini
        """
        self.client = AsyncOpenAI(api_key=openai_api_key)
        self.model = "gpt-4o-mini"

    async def generate_response(
        self,
        user_message: str,
        conversation_history: List[Dict[str, str]],
        retrieved_memories: List[Memory],
    ) -> AsyncIterator[str]:
        """
        Generate streaming response with memory context.

        Args:
            user_message: Current user message
            conversation_history: Recent conversation messages (list of {"role": "user"|"assistant", "content": "..."})
            retrieved_memories: Relevant memories retrieved from vector search

        Yields:
            str: Response tokens

        Raises:
            Exception: If OpenAI API call fails
        """
        try:
            # Build system prompt with memory context
            system_prompt = self._build_system_prompt(retrieved_memories)

            # Build messages array for OpenAI
            messages = [
                {"role": "system", "content": system_prompt},
                *conversation_history,  # Include recent history
                {"role": "user", "content": user_message},
            ]

            logger.info(
                f"Generating response for message with {len(retrieved_memories)} memories "
                f"and {len(conversation_history)} history messages"
            )

            # Stream response from OpenAI
            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=True,
                temperature=0.7,  # Balanced creativity
                max_tokens=1000,  # Reasonable response length
            )

            # Yield tokens as they arrive
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            logger.error(f"Error generating response: {type(e).__name__}: {str(e)}")
            raise

    def _build_system_prompt(self, memories: List[Memory]) -> str:
        """
        Build system prompt with memory context.

        Creates a comprehensive prompt that includes:
        - Eliza's core personality and principles
        - Relevant memories from the user's history
        - Behavioral guidelines

        Args:
            memories: Retrieved memories to include in context

        Returns:
            str: Complete system prompt
        """
        # Base personality prompt (from UX spec + "How Eliza Should Respond")
        base_prompt = """You are Eliza, an emotionally intelligent AI companion and guide.

Your Core Principles:
- **Empathy enables efficiency. Efficiency is the goal.** You understand feelings to diagnose blockers and unlock action.
- **Listen first, suggest second.** Validate struggles before offering solutions.
- **Distinguish controllable from uncontrollable stressors.** Help users focus energy where it matters.
- **Celebrate wins genuinely.** Progress deserves recognition.
- **Suggest circuit breakers when overwhelmed.** Rest and perspective are productivity tools.
- **Encourage momentum.** Small consistent actions compound into transformation.

Your Personality:
- Warm but directive
- Supportive without enabling avoidance
- Proactive: Ask questions, suggest goals, check in
- Adaptive: Match tone to user state (supportive, encouraging, urgent, celebratory)
- Contextual: Reference past conversations and show you remember

Communication Style:
- Be warm and conversational, not clinical
- Use "I remember..." when referencing past context
- Ask clarifying questions when needed
- Keep responses concise (2-4 sentences typically)
- Show genuine care and investment in their success"""

        # Add memory context if available
        if memories:
            memory_context = "\n\nWhat You Remember About This User:\n"
            for memory in memories:
                # Include memory content and type
                memory_type_label = memory.memory_type.value.upper()
                memory_context += f"- [{memory_type_label}] {memory.content}\n"

                # Include relevant metadata
                if memory.extra_data:
                    if memory.extra_data.get("stressor"):
                        memory_context += f"  (Stressor: {memory.extra_data.get('emotion', 'unspecified')})\n"
                    if memory.extra_data.get("goal_related"):
                        memory_context += f"  (Related to goal)\n"

            return base_prompt + memory_context

        return base_prompt
