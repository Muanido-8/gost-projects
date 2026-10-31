from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field

from ghost_projects.schemas.assessment import ProjectAssessment


class ReportFormat(str, Enum):
    MARKDOWN = "markdown"


class RecoveryReport(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    assessment: ProjectAssessment
    generated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    format: ReportFormat = ReportFormat.MARKDOWN