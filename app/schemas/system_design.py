"""Pydantic schemas for SystemDesign endpoints."""
from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, Field, field_validator

ComplexityLevel = Literal["beginner", "intermediate", "advanced"]


class SystemDesignBase(BaseModel):
    title: str = Field(..., min_length=5, max_length=500)
    description: str = Field(..., min_length=20, max_length=2000)
    stack: List[str] = Field(..., min_length=2, max_length=15)
    notes: List[str] = Field(..., min_length=2, max_length=10)
    diagram_url: Optional[str] = None
    diagram_type: Optional[str] = Field(None, max_length=50)
    complexity_level: ComplexityLevel

    @field_validator("stack")
    @classmethod
    def validate_stack(cls, v: List[str]) -> List[str]:
        if len(v) < 2 or len(v) > 15:
            raise ValueError("stack must contain 2-15 technologies")
        return v

    @field_validator("notes")
    @classmethod
    def validate_notes(cls, v: List[str]) -> List[str]:
        if len(v) < 2 or len(v) > 10:
            raise ValueError("notes must contain 2-10 key points")
        for note in v:
            if len(note) < 10 or len(note) > 500:
                raise ValueError("each note must be 10-500 characters")
        return v


class SystemDesignCreate(SystemDesignBase):
    pass


class SystemDesignUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=5, max_length=500)
    description: Optional[str] = Field(None, min_length=20, max_length=2000)
    stack: Optional[List[str]] = None
    notes: Optional[List[str]] = None
    diagram_url: Optional[str] = None
    diagram_type: Optional[str] = Field(None, max_length=50)
    complexity_level: Optional[ComplexityLevel] = None


class SystemDesignResponse(SystemDesignBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
