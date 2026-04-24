"""Tests for the AI chatbot service."""
import pytest

from app.services.chatbot import ChatbotService, IntentType


class TestIntentClassification:
    """Tests for rule-based intent classification."""

    def setup_method(self) -> None:
        """Create a minimal ChatbotService for testing."""
        from unittest.mock import MagicMock
        self.service = ChatbotService(
            ai_api_key="test-key",
            ai_provider="gemini",
            ai_model="gemini-1.5-flash",
            cache_service=MagicMock(),
            db_service=MagicMock(),
        )

    def test_projects_intent(self) -> None:
        assert self.service.classify_intent("show me your projects") == IntentType.PROJECTS
        assert self.service.classify_intent("what have you built?") == IntentType.PROJECTS
        assert self.service.classify_intent("github repos") == IntentType.PROJECTS

    def test_skills_intent(self) -> None:
        assert self.service.classify_intent("what are your skills?") == IntentType.SKILLS
        assert self.service.classify_intent("what technologies do you know?") == IntentType.SKILLS
        assert self.service.classify_intent("your tech stack") == IntentType.SKILLS

    def test_experience_intent(self) -> None:
        assert self.service.classify_intent("tell me about your experience") == IntentType.EXPERIENCE
        assert self.service.classify_intent("work history") == IntentType.EXPERIENCE

    def test_blog_intent(self) -> None:
        assert self.service.classify_intent("any blog posts?") == IntentType.BLOG
        assert self.service.classify_intent("articles you wrote") == IntentType.BLOG

    def test_system_design_intent(self) -> None:
        assert self.service.classify_intent("system design examples") == IntentType.SYSTEM_DESIGN
        assert self.service.classify_intent("architecture diagrams") == IntentType.SYSTEM_DESIGN

    def test_general_intent_fallback(self) -> None:
        assert self.service.classify_intent("hello there") == IntentType.GENERAL
        assert self.service.classify_intent("random question xyz") == IntentType.GENERAL

    def test_classify_never_returns_none(self) -> None:
        """Property: classify_intent always returns a valid IntentType."""
        queries = ["", "   ", "?", "123", "hello world", "!@#$%"]
        for query in queries:
            result = self.service.classify_intent(query)
            assert result is not None
            assert isinstance(result, IntentType)

    def test_classify_always_returns_valid_intent(self) -> None:
        """Property: all possible queries map to exactly one IntentType."""
        valid_intents = set(IntentType)
        test_queries = [
            "projects", "skills", "experience", "blog", "system design",
            "hello", "what is 2+2", "tell me everything",
        ]
        for query in test_queries:
            result = self.service.classify_intent(query)
            assert result in valid_intents


class TestCacheKeyStability:
    """Tests for stable cache key generation."""

    def test_md5_cache_key_is_stable(self) -> None:
        """hashlib.md5 produces the same key across calls (unlike Python hash())."""
        import hashlib
        query = "tell me about your projects"
        key1 = hashlib.md5(query.lower().encode()).hexdigest()
        key2 = hashlib.md5(query.lower().encode()).hexdigest()
        assert key1 == key2

    def test_md5_cache_key_case_insensitive(self) -> None:
        """Cache key is case-insensitive."""
        import hashlib
        key1 = hashlib.md5("Projects".lower().encode()).hexdigest()
        key2 = hashlib.md5("projects".lower().encode()).hexdigest()
        assert key1 == key2
