"""Pydantic schemas for Analytics."""
import ipaddress
from datetime import datetime
from typing import Any, Dict, Literal, Optional

from pydantic import BaseModel, Field, field_validator

EventType = Literal["page_view", "api_request", "chatbot_query"]


class AnalyticsCreate(BaseModel):
    event_type: EventType
    resource_type: Optional[str] = Field(None, max_length=50)
    resource_id: Optional[int] = None
    user_agent: Optional[str] = Field(None, max_length=500)
    ip_address: Optional[str] = Field(None, max_length=45)
    metadata: Optional[Dict[str, Any]] = None

    @field_validator("ip_address")
    @classmethod
    def validate_ip(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        try:
            ipaddress.ip_address(v)
        except ValueError:
            raise ValueError("ip_address must be a valid IPv4 or IPv6 address")
        return v


class AnalyticsResponse(AnalyticsCreate):
    id: int
    timestamp: datetime

    model_config = {"from_attributes": True}
