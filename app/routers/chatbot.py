"""AI Chatbot endpoint."""
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.cache import get_cache
from app.core.database import get_db
from app.core.logging import get_logger
from app.models.profile import Profile
from app.schemas.chatbot import ChatbotDefaultQuestionsResponse, ChatbotRequest, ChatbotResponse
from app.services.cache import CacheService
from app.services.chatbot import get_chatbot_service
from app.services.database import DatabaseService

router = APIRouter(prefix="/api/v1/chatbot", tags=["chatbot"])
logger = get_logger(__name__)


@router.post("/query", response_model=ChatbotResponse)
async def chatbot_query(
    request_data: ChatbotRequest,
    request: Request,
    session: AsyncSession = Depends(get_db),
    cache: CacheService = Depends(get_cache),
) -> ChatbotResponse:
    """
    Process a chatbot query.
    Uses hybrid approach: rule-based intent classification first,
    then Gemini API for complex queries.
    No authentication required — public endpoint.
    """
    db = DatabaseService(session)
    chatbot = get_chatbot_service(cache, db)

    result = await chatbot.process_query(
        query=request_data.query,
        session_id=str(request_data.session_id),
        request=request,
    )

    logger.info(
        "chatbot_query_processed",
        intent=result.get("intent"),
        session_id=str(request_data.session_id)[:8],
    )

    return ChatbotResponse(**result)


@router.get("/default-questions", response_model=ChatbotDefaultQuestionsResponse)
async def get_default_questions(
    session: AsyncSession = Depends(get_db),
    cache: CacheService = Depends(get_cache),
) -> ChatbotDefaultQuestionsResponse:
    """
    Get default chatbot questions from profile.
    Public endpoint, cached for 5 minutes.
    """
    cache_key = "chatbot:default_questions"
    cached = await cache.get(cache_key)
    
    if cached:
        import json
        return ChatbotDefaultQuestionsResponse(default_questions=json.loads(cached))
    
    db = DatabaseService(session)
    profile = await db.get_by_id(Profile, 1)
    
    default_questions = [
        "What projects have you built?",
        "What are your core skills?",
        "Tell me about your experience"
    ]
    
    if profile and profile.chatbot_default_questions:
        default_questions = profile.chatbot_default_questions
    
    await cache.set(cache_key, default_questions, ttl=300)  # 5 minutes
    
    return ChatbotDefaultQuestionsResponse(default_questions=default_questions)
