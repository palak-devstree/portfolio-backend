"""Pydantic schemas for AI Chatbot endpoint."""
from typing import List
from uuid import UUID

from pydantic import BaseModel, Field


class ChatbotRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500)
    session_id: UUID


class ChatbotResponse(BaseModel):
    message: str
    intent: str
    suggestions: List[str] = []


class ChatbotDefaultQuestionsResponse(BaseModel):
    """Response schema for fetching default chatbot questions."""
    default_questions: List[str]
