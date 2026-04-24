"""LabExperiment SQLAlchemy model."""
import enum
from datetime import datetime

from sqlalchemy import ARRAY, Column, DateTime, Enum, Integer, String, Text

from app.core.database import Base


class ExperimentStatus(str, enum.Enum):
    EXPERIMENTING = "experimenting"
    TESTING = "testing"
    COMPLETED = "completed"


class LabExperiment(Base):
    """Lab experiment model."""

    __tablename__ = "lab_experiments"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=False)
    stack = Column(ARRAY(String), nullable=False)
    status = Column(
        Enum(ExperimentStatus, name="experimentstatus", values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=ExperimentStatus.EXPERIMENTING,
    )
    findings = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<LabExperiment id={self.id} title={self.title!r} status={self.status}>"
