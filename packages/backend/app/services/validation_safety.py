"""
ValidationSafety - Content filtering, fact verification, and safety checks

Features:
- Content filtering (offensive content, harmful instructions)
- Fact verification with source citations
- Domain whitelisting/blacklisting for web search
- PII detection and masking
- Adjustable safety levels based on user preferences

Safety Levels:
- LOW: Minimal filtering, trust user
- MEDIUM: Standard filtering, block obvious issues
- HIGH: Strict filtering, verify facts, require sources

Usage:
    safety = get_validation_safety()

    # Check if content is safe
    is_safe, reason = await safety.validate_content(
        db, user_id, "User input text", direction="input"
    )

    # Verify a fact with sources
    verified, confidence, sources = await safety.verify_fact(
        "The Earth is flat", require_sources=True
    )
"""

import logging
import re
from enum import Enum
from typing import Dict, List, Optional, Tuple
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user_preferences import AgentPreferences

logger = logging.getLogger(__name__)


class SafetyLevel(str, Enum):
    """Content filtering strictness levels"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ContentDirection(str, Enum):
    """Direction of content flow"""

    INPUT = "input"  # User input to AI
    OUTPUT = "output"  # AI output to user


class ValidationSafety:
    """Service for content validation and safety checks"""

    def __init__(self):
        """Initialize validation and safety service"""
        # Offensive/harmful patterns (simplified - would use ML models in production)
        self.offensive_patterns = [
            r"\b(kill|harm|hurt)\s+(yourself|myself)\b",
            r"\b(suicide|self-harm)\s+(instruction|guide|how)\b",
            # Add more patterns in production
        ]

        # PII patterns
        self.pii_patterns = {
            "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
            "phone": r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b",
            "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
            "credit_card": r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b",
        }

        # Common harmful instruction keywords
        self.harmful_keywords = [
            "exploit",
            "hack",
            "malware",
            "phishing",
            "scam",
            "illegal",
            "weapon",
            "explosive",
        ]

    async def get_user_safety_settings(
        self, db: AsyncSession, user_id: UUID
    ) -> Dict:
        """
        Load user's safety and validation settings

        Args:
            db: Database session
            user_id: User ID

        Returns:
            Dict with safety settings
        """
        result = await db.execute(
            db.query(AgentPreferences).filter(AgentPreferences.user_id == user_id)
        )
        prefs = result.scalar_one_or_none()

        if not prefs:
            # Return default settings
            return {
                "filter_level": SafetyLevel.MEDIUM,
                "fact_verification": {"enabled": False, "require_sources": False},
                "allowed_domains": [],
                "blocked_domains": [],
            }

        return {
            "filter_level": SafetyLevel(prefs.content_filter_level),
            "fact_verification": prefs.enable_fact_verification or {
                "enabled": False,
                "require_sources": False,
            },
            "allowed_domains": prefs.allowed_search_domains or [],
            "blocked_domains": prefs.blocked_search_domains or [],
        }

    def _check_offensive_content(
        self, text: str, safety_level: SafetyLevel
    ) -> Tuple[bool, Optional[str]]:
        """
        Check for offensive or harmful content

        Args:
            text: Text to check
            safety_level: Safety level to apply

        Returns:
            (is_safe, reason) - (False, reason) if content is blocked
        """
        # Skip for LOW safety level
        if safety_level == SafetyLevel.LOW:
            return (True, None)

        text_lower = text.lower()

        # Check offensive patterns
        for pattern in self.offensive_patterns:
            if re.search(pattern, text_lower, re.IGNORECASE):
                logger.warning(f"Blocked content matching pattern: {pattern}")
                return (
                    False,
                    "Content contains potentially harmful instructions or language",
                )

        # Check harmful keywords (only for HIGH level)
        if safety_level == SafetyLevel.HIGH:
            harmful_count = sum(
                1 for keyword in self.harmful_keywords if keyword in text_lower
            )

            # Block if multiple harmful keywords present
            if harmful_count >= 3:
                logger.warning(
                    f"Blocked content with {harmful_count} harmful keywords"
                )
                return (
                    False,
                    "Content contains multiple potentially harmful keywords",
                )

        return (True, None)

    def _detect_pii(self, text: str) -> Dict[str, List[str]]:
        """
        Detect personally identifiable information (PII)

        Args:
            text: Text to scan

        Returns:
            Dict mapping PII type to list of detected values
        """
        detected = {}

        for pii_type, pattern in self.pii_patterns.items():
            matches = re.findall(pattern, text)
            if matches:
                detected[pii_type] = matches

        return detected

    def mask_pii(self, text: str, pii_types: Optional[List[str]] = None) -> str:
        """
        Mask PII in text

        Args:
            text: Text to mask
            pii_types: Optional list of PII types to mask (default: all)

        Returns:
            Text with PII masked
        """
        masked_text = text
        types_to_mask = pii_types or list(self.pii_patterns.keys())

        for pii_type in types_to_mask:
            if pii_type not in self.pii_patterns:
                continue

            pattern = self.pii_patterns[pii_type]
            replacement = f"[{pii_type.upper()}_REDACTED]"
            masked_text = re.sub(pattern, replacement, masked_text)

        return masked_text

    async def validate_content(
        self,
        db: AsyncSession,
        user_id: UUID,
        content: str,
        direction: ContentDirection = ContentDirection.INPUT,
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate content for safety and appropriateness

        Args:
            db: Database session
            user_id: User ID (for loading preferences)
            content: Text to validate
            direction: INPUT (user→AI) or OUTPUT (AI→user)

        Returns:
            (is_valid, reason) - (False, reason) if blocked
        """
        # Load user safety settings
        settings = await self.get_user_safety_settings(db, user_id)
        safety_level = settings["filter_level"]

        # Check offensive content
        is_safe, reason = self._check_offensive_content(content, safety_level)
        if not is_safe:
            return (False, reason)

        # Detect PII (warn but don't block for MEDIUM/LOW)
        pii_detected = self._detect_pii(content)
        if pii_detected and safety_level == SafetyLevel.HIGH:
            logger.warning(f"PII detected in {direction} content: {list(pii_detected.keys())}")
            # Could block or mask - for now just log

        # Additional OUTPUT-specific checks
        if direction == ContentDirection.OUTPUT:
            # Check for hallucinations, verify facts, etc.
            # (Would implement with LLM verification in production)
            pass

        return (True, None)

    async def verify_fact(
        self,
        fact: str,
        require_sources: bool = False,
    ) -> Tuple[bool, float, List[str]]:
        """
        Verify a factual claim with optional source requirements

        Args:
            fact: Factual claim to verify
            require_sources: Require citation sources

        Returns:
            (is_verified, confidence, sources)
        """
        # TODO: Implement actual fact verification
        # This would use:
        # 1. Web search for corroborating sources
        # 2. LLM-based fact checking
        # 3. Knowledge graph cross-referencing

        # For now, return placeholder
        logger.info(f"Fact verification requested: {fact[:100]}...")

        # Placeholder implementation
        verified = True
        confidence = 0.8
        sources = [
            "https://example.com/source1" if require_sources else None,
            "https://example.com/source2" if require_sources else None,
        ]
        sources = [s for s in sources if s]  # Remove None values

        return (verified, confidence, sources)

    def validate_search_domain(
        self, url: str, allowed_domains: List[str], blocked_domains: List[str]
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate if a URL/domain is allowed for web search

        Args:
            url: URL to validate
            allowed_domains: Whitelist (empty = allow all)
            blocked_domains: Blacklist

        Returns:
            (is_allowed, reason) - (False, reason) if blocked
        """
        # Extract domain from URL
        domain_match = re.search(r"https?://([^/]+)", url)
        if not domain_match:
            return (False, "Invalid URL format")

        domain = domain_match.group(1).lower()

        # Check blacklist first
        for blocked in blocked_domains:
            if blocked.lower() in domain:
                logger.warning(f"Blocked search domain: {domain}")
                return (False, f"Domain {domain} is blocked by user preferences")

        # Check whitelist if configured
        if allowed_domains:
            allowed = any(allowed.lower() in domain for allowed in allowed_domains)
            if not allowed:
                logger.warning(f"Domain not in whitelist: {domain}")
                return (
                    False,
                    f"Domain {domain} is not in allowed domains list",
                )

        return (True, None)

    def sanitize_output(
        self, text: str, remove_pii: bool = False, max_length: Optional[int] = None
    ) -> str:
        """
        Sanitize AI output before sending to user

        Args:
            text: Output text
            remove_pii: Mask any detected PII
            max_length: Optional maximum length (truncate if exceeded)

        Returns:
            Sanitized text
        """
        sanitized = text

        # Remove PII if requested
        if remove_pii:
            sanitized = self.mask_pii(sanitized)

        # Truncate if too long
        if max_length and len(sanitized) > max_length:
            sanitized = sanitized[:max_length] + "..."
            logger.info(f"Truncated output from {len(text)} to {max_length} chars")

        return sanitized

    async def check_rate_limit(
        self, db: AsyncSession, user_id: UUID, action: str, limit: int, window_seconds: int
    ) -> Tuple[bool, Optional[str]]:
        """
        Check if user has exceeded rate limit for an action

        Args:
            db: Database session
            user_id: User ID
            action: Action type (e.g., "api_call", "memory_write")
            limit: Maximum actions allowed
            window_seconds: Time window in seconds

        Returns:
            (is_allowed, reason) - (False, reason) if rate limit exceeded
        """
        # TODO: Implement actual rate limiting using Redis
        # This would track:
        # - API calls per minute/hour
        # - Memory writes per hour
        # - Cost limits per day
        # - Token usage per request

        # For now, always allow
        return (True, None)


# Singleton instance
_validation_safety: Optional[ValidationSafety] = None


def get_validation_safety() -> ValidationSafety:
    """
    Get singleton instance of ValidationSafety

    Returns:
        ValidationSafety instance
    """
    global _validation_safety
    if _validation_safety is None:
        _validation_safety = ValidationSafety()
    return _validation_safety
