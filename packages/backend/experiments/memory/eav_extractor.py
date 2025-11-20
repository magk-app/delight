"""
Entity-Attribute-Value (EAV) Extraction for Hierarchical Memory

Extracts structured entity-attribute-value triples from user messages to enable
hierarchical memory storage and graph relationships.

Examples:
    Input: "I went to UCSB, MIT, and Georgia Tech"
    Output: Entity(jack_education) -> Attribute(universities) -> Value(["UCSB", "MIT", "Georgia Tech"])

    Input: "My favorite restaurant is Yoshinoya. I love their tonkatsu bowl for $10."
    Output: Entity(yoshinoya) -> {
        favorite_dish: "tonkatsu bowl",
        price: "$10",
        type: "restaurant"
    }
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from openai import AsyncOpenAI
from experiments.config import get_config


# ============================================================================
# Pydantic Models for Structured Output
# ============================================================================

class AttributeValue(BaseModel):
    """A single attribute-value pair."""
    attribute: str = Field(description="The attribute name (e.g., 'favorite_dish', 'price', 'location')")
    value: Any = Field(description="The value (can be string, number, list, or nested dict)")
    confidence: float = Field(description="Confidence in this extraction (0-1)", ge=0.0, le=1.0)


class Entity(BaseModel):
    """An entity with its attributes."""
    entity_name: str = Field(description="Entity identifier (e.g., 'jack_education', 'yoshinoya', 'delight_project')")
    entity_type: str = Field(description="Type of entity (e.g., 'person', 'place', 'project', 'organization')")
    attributes: List[AttributeValue] = Field(description="List of attribute-value pairs for this entity")
    related_entities: List[str] = Field(
        default_factory=list,
        description="IDs of related entities (e.g., 'jack' relates to 'delight_project')"
    )


class EAVExtractionResponse(BaseModel):
    """Complete EAV extraction result."""
    entities: List[Entity] = Field(description="List of extracted entities with their attributes")
    reasoning: str = Field(description="Explanation of extraction logic")


# ============================================================================
# EAV Extractor
# ============================================================================

class EAVExtractor:
    """Extract Entity-Attribute-Value triples for hierarchical memory storage.

    This extractor identifies:
    - Entities (people, places, projects, organizations)
    - Attributes (properties, characteristics, relationships)
    - Values (concrete data - strings, numbers, lists, nested objects)

    Example:
        >>> extractor = EAVExtractor()
        >>> result = await extractor.extract_eav(
        ...     "I went to UCSB, MIT, and Georgia Tech. "
        ...     "My favorite restaurant is Yoshinoya with tonkatsu for $10."
        ... )
        >>> len(result.entities)
        2  # jack_education and yoshinoya
    """

    SYSTEM_PROMPT = """You are an expert at extracting structured Entity-Attribute-Value (EAV) triples from text.

Your task is to identify entities, their attributes, and values in a way that enables hierarchical memory storage.

**Entity Types:**
- person: People, users, individuals
- place: Locations, cities, venues, buildings
- organization: Companies, schools, groups
- project: Work projects, initiatives
- object: Physical or conceptual objects (e.g., restaurant, car, app)
- event: Occurrences, activities, experiences

**Guidelines:**

1. **Entity Identification**: Create meaningful entity IDs (snake_case)
   - Use descriptive names: "jack_education", "yoshinoya_restaurant", "delight_project"
   - Not just "education" or "restaurant" - be specific!

2. **Hierarchical Attributes**: Group related attributes under entities
   - ✅ Entity: "jack_education" -> Attributes: {universities: ["UCSB", "MIT", "Georgia Tech"]}
   - ❌ Three separate facts: "went to UCSB", "went to MIT", "went to Georgia Tech"

3. **Complex Values**: Use lists, dicts, or nested structures when appropriate
   - Lists: ["item1", "item2", "item3"]
   - Nested: {name: "X", properties: {a: 1, b: 2}}

4. **Related Entities**: Link entities that reference each other
   - If "jack" works on "delight_project", both should reference each other

5. **Concrete Data Only**: Extract actual information, not questions or vague statements

**Examples:**

Example 1: Educational Background
Input: "I attended UCSB, MIT, and Georgia Tech for my degrees"

Output:
{
  "entities": [
    {
      "entity_name": "jack_education",
      "entity_type": "person",
      "attributes": [
        {
          "attribute": "universities",
          "value": ["UCSB", "MIT", "Georgia Tech"],
          "confidence": 0.95
        },
        {
          "attribute": "degree_status",
          "value": "completed",
          "confidence": 0.85
        }
      ],
      "related_entities": []
    }
  ],
  "reasoning": "Grouped multiple universities under single education entity for hierarchical storage"
}

Example 2: Restaurant Preferences
Input: "My favorite restaurant is Yoshinoya. I love their tonkatsu bowl, costs around $10, and they have locations in Tokyo and America."

Output:
{
  "entities": [
    {
      "entity_name": "yoshinoya",
      "entity_type": "place",
      "attributes": [
        {
          "attribute": "type",
          "value": "restaurant",
          "confidence": 0.99
        },
        {
          "attribute": "favorite_dish",
          "value": "tonkatsu bowl",
          "confidence": 0.95
        },
        {
          "attribute": "price",
          "value": "$10",
          "confidence": 0.90
        },
        {
          "attribute": "locations",
          "value": ["Tokyo", "America"],
          "confidence": 0.90
        },
        {
          "attribute": "user_preference",
          "value": "favorite",
          "confidence": 0.98
        }
      ],
      "related_entities": []
    }
  ],
  "reasoning": "Created single entity for restaurant with all attributes grouped hierarchically"
}

Example 3: Project Work
Input: "I'm working on Delight, an AI companion app. Built with Python and React. Launching Q1 2025."

Output:
{
  "entities": [
    {
      "entity_name": "delight_project",
      "entity_type": "project",
      "attributes": [
        {
          "attribute": "description",
          "value": "AI companion app",
          "confidence": 0.98
        },
        {
          "attribute": "tech_stack",
          "value": ["Python", "React"],
          "confidence": 0.95
        },
        {
          "attribute": "launch_timeline",
          "value": "Q1 2025",
          "confidence": 0.92
        },
        {
          "attribute": "status",
          "value": "in_progress",
          "confidence": 0.85
        }
      ],
      "related_entities": []
    }
  ],
  "reasoning": "Grouped all project attributes under single entity for better organization"
}

Now extract EAV triples from the user's message."""

    def __init__(self):
        """Initialize EAV extractor."""
        self.config = get_config()
        if not self.config.openai_api_key:
            raise ValueError("OPENAI_API_KEY not set in environment")

        self.client = AsyncOpenAI(api_key=self.config.openai_api_key)
        self.model = self.config.chat_model  # gpt-4o-mini

        # Statistics
        self.total_extractions = 0
        self.total_entities_extracted = 0

    async def extract_eav(
        self,
        message: str,
        context_entities: Optional[List[str]] = None
    ) -> EAVExtractionResponse:
        """Extract Entity-Attribute-Value triples from message.

        Args:
            message: User message to extract from
            context_entities: Optional list of known entity IDs for context

        Returns:
            EAVExtractionResponse with entities and attributes

        Example:
            >>> result = await extractor.extract_eav(
            ...     "I studied at MIT and UCSB"
            ... )
            >>> result.entities[0].entity_name
            'jack_education'
            >>> result.entities[0].attributes[0].attribute
            'universities'
            >>> result.entities[0].attributes[0].value
            ['MIT', 'UCSB']
        """
        if not message or not message.strip():
            raise ValueError("Message cannot be empty")

        # Build prompt
        user_prompt = f"Extract EAV triples from this message:\n\n{message}"

        if context_entities:
            user_prompt += f"\n\nKnown entities: {', '.join(context_entities)}"

        try:
            response = await self.client.beta.chat.completions.parse(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                response_format=EAVExtractionResponse,
                temperature=0.3
            )

            result = response.choices[0].message.parsed

            # Update statistics
            self.total_extractions += 1
            self.total_entities_extracted += len(result.entities)

            return result

        except Exception as e:
            print(f"❌ Error extracting EAV: {e}")
            raise

    def print_eav_summary(self, result: EAVExtractionResponse):
        """Print formatted EAV extraction summary."""
        print("\n" + "=" * 70)
        print("📊 Entity-Attribute-Value Extraction Summary")
        print("=" * 70)
        print(f"Entities Extracted: {len(result.entities)}\n")

        for i, entity in enumerate(result.entities, 1):
            print(f"{i}. Entity: {entity.entity_name} ({entity.entity_type})")
            print("   Attributes:")
            for attr in entity.attributes:
                value_str = str(attr.value)
                if len(value_str) > 60:
                    value_str = value_str[:60] + "..."
                print(f"     - {attr.attribute}: {value_str} (confidence: {attr.confidence:.2f})")

            if entity.related_entities:
                print(f"   Related: {', '.join(entity.related_entities)}")
            print()

        print(f"Reasoning: {result.reasoning}")
        print("=" * 70 + "\n")

    def get_statistics(self) -> dict:
        """Get extractor statistics."""
        return {
            "total_extractions": self.total_extractions,
            "total_entities_extracted": self.total_entities_extracted,
            "avg_entities_per_extraction": (
                self.total_entities_extracted / self.total_extractions
                if self.total_extractions > 0
                else 0
            )
        }


# ============================================================================
# Convenience Functions
# ============================================================================

async def quick_extract_eav(message: str) -> List[Entity]:
    """Quick EAV extraction without creating extractor instance."""
    extractor = EAVExtractor()
    result = await extractor.extract_eav(message)
    return result.entities


if __name__ == "__main__":
    """Test EAV extraction."""
    import asyncio

    async def test():
        extractor = EAVExtractor()

        test_messages = [
            "I attended UCSB, MIT, and Georgia Tech",
            "My favorite restaurant is Yoshinoya. I love their tonkatsu bowl for $10, and they have locations in Tokyo and America",
            "I'm working on Delight, an AI companion app built with Python and React. Launching Q1 2025.",
            "I prefer TypeScript over JavaScript. I work late nights and drink lots of coffee.",
        ]

        for msg in test_messages:
            print("\n" + "="*80)
            print(f"Input: {msg}\n")
            result = await extractor.extract_eav(msg)
            extractor.print_eav_summary(result)

        # Print stats
        stats = extractor.get_statistics()
        print("\n📈 Statistics:")
        print(f"   Total Extractions: {stats['total_extractions']}")
        print(f"   Total Entities: {stats['total_entities_extracted']}")
        print(f"   Avg Entities/Extraction: {stats['avg_entities_per_extraction']:.2f}")

    asyncio.run(test())
