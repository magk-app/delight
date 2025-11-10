"""
Example Unit Tests
Fast, isolated tests with no external dependencies

These tests demonstrate unit testing patterns for business logic,
utility functions, and pure functions.
"""

import pytest


# ============================================================================
# Example: Testing Pure Functions
# ============================================================================

def example_calculate_progress_percentage(completed: int, total: int) -> float:
    """Example function to test"""
    if total == 0:
        return 0.0
    return round((completed / total) * 100, 2)


class TestProgressCalculations:
    """Test suite for progress calculation functions"""
    
    def test_calculate_progress_percentage_normal(self):
        """Should calculate percentage correctly"""
        result = example_calculate_progress_percentage(5, 10)
        assert result == 50.0
    
    def test_calculate_progress_percentage_complete(self):
        """Should return 100 when all complete"""
        result = example_calculate_progress_percentage(10, 10)
        assert result == 100.0
    
    def test_calculate_progress_percentage_zero_total(self):
        """Should handle zero total gracefully"""
        result = example_calculate_progress_percentage(5, 0)
        assert result == 0.0
    
    def test_calculate_progress_percentage_rounding(self):
        """Should round to 2 decimal places"""
        result = example_calculate_progress_percentage(1, 3)
        assert result == 33.33


# ============================================================================
# Example: Testing Business Logic
# ============================================================================

def example_validate_quest_type(quest_type: str) -> bool:
    """Example validation function"""
    valid_types = {"short_term", "long_term", "epic"}
    return quest_type in valid_types


@pytest.mark.unit
class TestQuestValidation:
    """Test suite for quest validation logic"""
    
    @pytest.mark.parametrize("quest_type,expected", [
        ("short_term", True),
        ("long_term", True),
        ("epic", True),
        ("invalid", False),
        ("", False),
    ])
    def test_validate_quest_type(self, quest_type, expected):
        """Should validate quest types correctly"""
        result = example_validate_quest_type(quest_type)
        assert result == expected


# ============================================================================
# Example: Testing Data Models (Pydantic Schemas)
# ============================================================================

from pydantic import BaseModel, ValidationError


class ExampleQuestSchema(BaseModel):
    """Example Pydantic schema for testing"""
    title: str
    description: str
    type: str


@pytest.mark.unit
class TestQuestSchema:
    """Test suite for Pydantic schema validation"""
    
    def test_valid_schema(self):
        """Should accept valid data"""
        data = {
            "title": "Learn Python",
            "description": "Master Python fundamentals",
            "type": "short_term"
        }
        quest = ExampleQuestSchema(**data)
        assert quest.title == "Learn Python"
    
    def test_missing_required_field(self):
        """Should reject missing required fields"""
        data = {"title": "Learn Python"}
        with pytest.raises(ValidationError):
            ExampleQuestSchema(**data)


# ============================================================================
# Running Tests
# ============================================================================
# Run with: poetry run pytest tests/unit/test_example.py -v
# Run unit tests only: poetry run pytest -m unit

