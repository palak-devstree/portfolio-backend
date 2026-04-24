"""AI Chatbot endpoint."""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.cache import get_cache
from app.core.database import get_db
from app.core.logging import get_logger
from app.schemas.chatbot import ChatbotRequest, ChatbotResponse
from app.services.cache import CacheService
from app.services.chatbot import get_chatbot_service
from app.services.database import DatabaseService

router = APIRouter(prefix="/api/v1/chatbot", tags=["chatbot"])
logger = get_logger(__name__)


@router.post("/query", response_model=ChatbotResponse)
async def chatbot_query(
    request: ChatbotRequest,
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
        query=request.query,
        session_id=str(request.session_id),
    )

    logger.info(
        "chatbot_query_processed",
        intent=result.get("intent"),
        session_id=str(request.session_id)[:8],
    )

    return ChatbotResponse(**result)
