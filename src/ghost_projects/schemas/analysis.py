from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, model_validator

from ghost_projects.schemas.assessment import ProjectAssessment
from ghost_projects.schemas.project import ProjectInfo


class AnalysisStatus(str, Enum):
    PENDING = "pending"
    SCANNING = "scanning"
    ANALYZING = "analyzing"
    COMPLETED = "completed"
    FAILED = "failed"


class AnalysisResult(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    project: ProjectInfo
    status: AnalysisStatus = AnalysisStatus.PENDING
    assessment: ProjectAssessment | None = None

    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)

    started_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    finished_at: datetime | None = None

    @model_validator(mode="after")
    def validate_final_state(self) -> "AnalysisResult":
        if self.status == AnalysisStatus.COMPLETED:
            if self.assessment is None:
                raise ValueError(
                    "A completed analysis must have an assessment"
                )

            if self.finished_at is None:
                raise ValueError(
                    "A completed analysis must have a finish time"
                )

        if self.status == AnalysisStatus.FAILED and not self.errors:
            raise ValueError(
                "A failed analysis must contain at least one error"
            )

        if (
            self.finished_at is not None
            and self.finished_at < self.started_at
        ):
            raise ValueError(
                "finished_at cannot be earlier than started_at"
            )

        return self