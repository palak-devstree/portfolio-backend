"""AI Chatbot service — hybrid rule-based + Gemini/OpenAI."""
import hashlib
import re
from enum import Enum
from typing import Any, Dict, List, Optional

from fastapi import Request

from app.core.config import settings
from app.core.logging import get_logger
from app.models.chatbot_query import ChatbotQuery
from app.models.profile import Profile
from app.services.analytics import anonymize_ip, get_client_ip
from app.services.cache import CacheService
from app.services.database import DatabaseService

logger = get_logger(__name__)


class IntentType(str, Enum):
    GREETING = "greeting"
    PROJECTS = "projects"
    SKILLS = "skills"
    EXPERIENCE = "experience"
    SYSTEM_DESIGN = "system_design"
    BLOG = "blog"
    GENERAL = "general"


class AIProvider(str, Enum):
    GEMINI = "gemini"
    OPENAI = "openai"


# Suggestions per intent
INTENT_SUGGESTIONS: Dict[IntentType, List[str]] = {
    IntentType.GREETING: ["Ask about projects", "Ask about skills", "Ask about experience"],
    IntentType.PROJECTS: ["Ask about skills", "Ask about system design", "Ask about blog posts"],
    IntentType.SKILLS: ["Ask about projects", "Ask about experience", "Ask about system design"],
    IntentType.EXPERIENCE: ["Ask about projects", "Ask about skills", "Ask about blog posts"],
    IntentType.SYSTEM_DESIGN: ["Ask about projects", "Ask about skills", "Ask about experience"],
    IntentType.BLOG: ["Ask about projects", "Ask about system design", "Ask about skills"],
    IntentType.GENERAL: ["Ask about projects", "Ask about skills", "Ask about blog posts"],
}


# Static greeting responses
GREETING_RESPONSES = [
    "Hi! I'm here to help you learn more about this portfolio. What would you like to know?",
    "Hello! Feel free to ask me about projects, skills, experience, or anything else!",
    "Hey there! I can answer questions about the work showcased here. What interests you?",
]


class ChatbotService:
    """
    Hybrid chatbot combining rule-based intent classification (zero cost)
    with Google Gemini API for complex queries (1500 req/day free).
    Switchable AI provider via config (Gemini default, OpenAI alternative).
    """

    def __init__(
        self,
        ai_api_key: str,
        ai_provider: AIProvider,
        ai_model: str,
        cache_service: CacheService,
        db_service: DatabaseService,
    ) -> None:
        self.ai_api_key = ai_api_key
        self.ai_provider = ai_provider
        self.ai_model = ai_model
        self.cache = cache_service
        self.db = db_service
        self.intent_patterns = self._load_intent_patterns()

    def _load_intent_patterns(self) -> Dict[IntentType, List[str]]:
        """Load regex patterns for intent classification."""
        return {
            IntentType.GREETING: [
                r"^(hi|hello|hey|greetings|good\s+(morning|afternoon|evening))[\s!.?]*$",
                r"^(what'?s\s+up|howdy|yo)[\s!.?]*$",
            ],
            IntentType.PROJECTS: [
                r"\bproject[s]?\b",
                r"\bbuilt?\b",
                r"\bcreated?\b",
                r"\bdeveloped?\b",
                r"\bgithub\b",
                r"\brepository\b",
                r"\brepo[s]?\b",
                r"\bportfolio\b",
                r"\bwork\b.*\bshow\b",
            ],
            IntentType.SKILLS: [
                r"\bskill[s]?\b",
                r"\btechnology\b",
                r"\btechnolog(?:y|ies)\b",
                r"\bstack\b",
                r"\bprogramming\b",
                r"\blanguage[s]?\b",
                r"\bframework[s]?\b",
                r"\btools?\b",
                r"\bexpertise\b",
                r"\bproficient\b",
                r"\bknow\b.*\bwhat\b",
            ],
            IntentType.EXPERIENCE: [
                r"\bexperience\b",
                r"\bwork(?:ed|ing)?\b",
                r"\bjob[s]?\b",
                r"\bcareer\b",
                r"\bbackground\b",
                r"\bhistory\b",
                r"\byear[s]?\b.*\bexperience\b",
                r"\bprevious\b",
            ],
            IntentType.SYSTEM_DESIGN: [
                r"\bsystem\s+design\b",
                r"\barchitecture\b",
                r"\bdesign\b.*\bpattern[s]?\b",
                r"\bscalability\b",
                r"\bscalable\b",
                r"\bdistributed\b",
                r"\bmicroservice[s]?\b",
                r"\bdiagram[s]?\b",
            ],
            IntentType.BLOG: [
                r"\bblog[s]?\b",
                r"\barticle[s]?\b",
                r"\bpost[s]?\b",
                r"\bwrit(?:e|ing|ten)\b",
                r"\bpublished?\b",
                r"\bread\b.*\bmore\b",
            ],
        }

    def classify_intent(self, query: str) -> IntentType:
        """
        Classify query intent using regex pattern matching.
        Returns IntentType.GENERAL if no pattern matches.
        Time complexity: O(p * m) where p = patterns, m = match complexity.
        """
        query_lower = query.lower().strip()

        for intent_type, pattern_list in self.intent_patterns.items():
            for pattern in pattern_list:
                if re.search(pattern, query_lower):
                    return intent_type

        return IntentType.GENERAL

    async def process_query(self, query: str, session_id: str, request: Request) -> Dict[str, Any]:
        """
        Process a chatbot query with hybrid approach.
        1. Classify intent (rule-based, zero cost)
        2. Handle greetings with static responses (no AI call)
        3. Check cache (hashlib.md5 for stable cross-process keys)
        4. Handle simple intents from DB; complex via AI API
        5. Track query and response in database
        6. Cache response and update session
        """
        intent = self.classify_intent(query)

        # Get default questions from profile
        default_questions = await self._get_default_questions()

        # Handle greetings with static response (no AI call)
        if intent == IntentType.GREETING:
            import random
            response = {
                "message": random.choice(GREETING_RESPONSES),
                "intent": intent.value,
                "suggestions": default_questions,
            }
            await self._track_query(query, response, session_id, request)
            return response

        # Stable cache key using hashlib.md5 (NOT Python built-in hash())
        query_hash = hashlib.md5(query.lower().encode()).hexdigest()
        cache_key = f"chatbot:query:{query_hash}"

        cached = await self.cache.get(cache_key)
        if cached:
            logger.info("chatbot_cache_hit", query_hash=query_hash)
            import json
            response = json.loads(cached)
            await self._track_query(query, response, session_id, request)
            return response

        # Route to appropriate handler
        if intent in [
            IntentType.PROJECTS,
            IntentType.SKILLS,
            IntentType.EXPERIENCE,
            IntentType.BLOG,
            IntentType.SYSTEM_DESIGN,
        ]:
            response = await self.handle_simple_query(intent, query)
            await self.cache.set(cache_key, response, ttl=3600)  # 1 hour
        else:
            response = await self.handle_complex_query(query, intent)
            await self.cache.set(cache_key, response, ttl=1800)  # 30 min

        # Track query in database
        await self._track_query(query, response, session_id, request)

        # Update session context
        await self.cache.set(
            f"session:{session_id}:last_query", query, ttl=3600
        )

        return response

    async def handle_simple_query(
        self, intent: IntentType, query: str
    ) -> Dict[str, Any]:
        """Handle simple intents by fetching data from DB."""
        context = await self.get_context_data(intent)
        message = self._format_simple_response(intent, context)
        return {
            "message": message,
            "intent": intent.value,
            "suggestions": INTENT_SUGGESTIONS.get(intent, []),
        }

    async def handle_complex_query(
        self, query: str, intent: IntentType
    ) -> Dict[str, Any]:
        """Handle complex queries via AI API with fallback to rule-based."""
        try:
            context = await self.get_context_data(IntentType.GENERAL)
            prompt = self._build_ai_prompt(query, context)
            ai_message = await self._call_ai_api(prompt)
            return {
                "message": ai_message,
                "intent": intent.value,
                "suggestions": INTENT_SUGGESTIONS[IntentType.GENERAL],
            }
        except Exception as exc:
            logger.warning("ai_api_failed_fallback", error=str(exc))
            return {
                "message": (
                    "I'm currently in simplified mode. I can still help with questions "
                    "about projects, skills, experience, blog posts, and system designs."
                ),
                "intent": IntentType.GENERAL.value,
                "suggestions": INTENT_SUGGESTIONS[IntentType.GENERAL],
            }

    async def get_context_data(self, intent: IntentType) -> Dict[str, Any]:
        """Fetch relevant context data from the database for the given intent."""
        from app.models.blog_post import BlogPost
        from app.models.project import Project, ProjectStatus
        from app.models.system_design import SystemDesign

        context: Dict[str, Any] = {}

        try:
            if intent in [IntentType.PROJECTS, IntentType.GENERAL]:
                projects = await self.db.get_all(
                    Project,
                    limit=10,
                    filters={"status": ProjectStatus.DONE},
                )
                context["projects"] = [
                    {"name": p.name, "description": p.description, "stack": p.stack}
                    for p in projects
                ]

            if intent in [IntentType.BLOG, IntentType.GENERAL]:
                posts = await self.db.get_all(
                    BlogPost, limit=5, filters={"is_published": True}
                )
                context["blog_posts"] = [
                    {"title": p.title, "preview": p.preview, "tags": p.tags}
                    for p in posts
                ]

            if intent in [IntentType.SYSTEM_DESIGN, IntentType.GENERAL]:
                designs = await self.db.get_all(SystemDesign, limit=5)
                context["system_designs"] = [
                    {"title": d.title, "description": d.description, "stack": d.stack}
                    for d in designs
                ]
        except Exception as exc:
            logger.warning("chatbot_context_fetch_failed", error=str(exc))

        return context

    def _format_simple_response(
        self, intent: IntentType, context: Dict[str, Any]
    ) -> str:
        """Format a structured response from DB context data."""
        if intent == IntentType.PROJECTS:
            projects = context.get("projects", [])
            if not projects:
                return "I don't have any completed projects listed yet, but check back soon!"
            names = ", ".join(p["name"] for p in projects[:5])
            return (
                f"I have {len(projects)} completed projects including: {names}. "
                "Each showcases different aspects of backend engineering. "
                "Would you like to know more about any specific project?"
            )

        if intent == IntentType.SKILLS:
            return (
                "My core skills include Python, FastAPI, PostgreSQL, Redis, Docker, "
                "and cloud infrastructure. I specialize in backend systems, API design, "
                "distributed systems, and AI/ML integration. "
                "Ask me about specific technologies or projects!"
            )

        if intent == IntentType.EXPERIENCE:
            return (
                "I'm a backend engineer with experience building scalable APIs, "
                "distributed systems, and AI-powered applications. "
                "I focus on pragmatic engineering — building production-quality systems "
                "within real-world constraints. Ask about specific projects or skills!"
            )

        if intent == IntentType.BLOG:
            posts = context.get("blog_posts", [])
            if not posts:
                return "No blog posts published yet — stay tuned!"
            titles = ", ".join(f'"{p["title"]}"' for p in posts[:3])
            return (
                f"I've written {len(posts)} blog posts including: {titles}. "
                "Topics cover backend engineering, system design, and AI integration."
            )

        if intent == IntentType.SYSTEM_DESIGN:
            designs = context.get("system_designs", [])
            if not designs:
                return "No system design case studies published yet."
            titles = ", ".join(d["title"] for d in designs[:3])
            return (
                f"I have {len(designs)} system design case studies including: {titles}. "
                "These cover scalable architectures, distributed systems, and design patterns."
            )

        return "I can help with questions about projects, skills, experience, blog posts, and system designs!"

    def _build_ai_prompt(self, query: str, context: Dict[str, Any]) -> str:
        """Build a prompt for the AI API with portfolio context."""
        context_str = ""
        if context.get("projects"):
            project_names = [p["name"] for p in context["projects"][:5]]
            context_str += f"Projects: {', '.join(project_names)}. "
        if context.get("blog_posts"):
            post_titles = [p["title"] for p in context["blog_posts"][:3]]
            context_str += f"Blog posts: {', '.join(post_titles)}. "

        return (
            f"You are an AI assistant for a backend engineer's portfolio website. "
            f"Portfolio context: {context_str}"
            f"Answer this question concisely and helpfully: {query}"
        )

    async def _call_ai_api(self, prompt: str) -> str:
        """Call the configured AI provider (Gemini or OpenAI)."""
        if self.ai_provider == AIProvider.GEMINI:
            return await self._call_gemini(prompt)
        elif self.ai_provider == AIProvider.OPENAI:
            return await self._call_openai(prompt)
        raise ValueError(f"Unknown AI provider: {self.ai_provider}")

    async def _call_gemini(self, prompt: str) -> str:
        """Call Google Gemini API."""
        import google.generativeai as genai

        genai.configure(api_key=self.ai_api_key)
        model = genai.GenerativeModel(self.ai_model)
        response = model.generate_content(prompt)
        return response.text

    async def _call_openai(self, prompt: str) -> str:
        """Call OpenAI API."""
        from openai import AsyncOpenAI

        client = AsyncOpenAI(api_key=self.ai_api_key)
        response = await client.chat.completions.create(
            model=self.ai_model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
        )
        return response.choices[0].message.content or ""

    async def _get_default_questions(self) -> List[str]:
        """Fetch default chatbot questions from profile."""
        try:
            profile = await self.db.get_by_id(Profile, 1)
            if profile and profile.chatbot_default_questions:
                return profile.chatbot_default_questions
        except Exception as exc:
            logger.warning("failed_to_fetch_default_questions", error=str(exc))
        
        # Fallback to default questions
        return [
            "What projects have you built?",
            "What are your core skills?",
            "Tell me about your experience"
        ]

    async def _track_query(
        self, query: str, response: Dict[str, Any], session_id: str, request: Request
    ) -> None:
        """Track chatbot query and response in database."""
        try:
            raw_ip = get_client_ip(request)
            anon_ip = anonymize_ip(raw_ip) if raw_ip else None

            chatbot_query = ChatbotQuery(
                session_id=session_id,
                query=query,
                response=response.get("message", ""),
                intent=response.get("intent", "general"),
                ip_address=anon_ip,
                user_agent=request.headers.get("User-Agent", "")[:500],
            )

            await self.db.create(chatbot_query)
        except Exception as exc:
            logger.warning("chatbot_query_tracking_failed", error=str(exc))


def get_chatbot_service(
    cache_service: CacheService,
    db_service: DatabaseService,
) -> ChatbotService:
    """Factory function to create a ChatbotService."""
    provider = AIProvider(settings.AI_PROVIDER.lower())
    return ChatbotService(
        ai_api_key=settings.AI_API_KEY,
        ai_provider=provider,
        ai_model=settings.AI_MODEL,
        cache_service=cache_service,
        db_service=db_service,
    )
