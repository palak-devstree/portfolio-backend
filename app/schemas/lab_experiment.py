"""Pydantic schemas for LabExperiment endpoints."""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator

from app.models.lab_experiment import ExperimentStatus


class LabExperimentBase(BaseModel):
    title: str = Field(..., min_length=5, max_length=500)
    description: str = Field(..., min_length=20, max_length=2000)
    stack: List[str] = Field(..., min_length=1, max_length=10)
    status: ExperimentStatus = ExperimentStatus.EXPERIMENTING
    findings: Optional[str] = None

    @field_validator("stack")
    @classmethod
    def validate_stack(cls, v: List[str]) -> List[str]:
        if len(v) < 1 or len(v) > 10:
            raise ValueError("stack must contain 1-10 technologies")
        return v


class LabExperimentCreate(LabExperimentBase):
    pass


class LabExperimentUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=5, max_length=500)
    description: Optional[str] = Field(None, min_length=20, max_length=2000)
    stack: Optional[List[str]] = None
    status: Optional[ExperimentStatus] = None
    findings: Optional[str] = None


class LabExperimentResponse(LabExperimentBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
