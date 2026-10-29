from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class FindingCategory(str, Enum):
    PROJECT_PURPOSE = "project_purpose"
    INCOMPLETE_FEATURE = "incomplete_feature"
    SETUP_PROBLEM = "setup_problem"
    BUG_OR_RISK = "bug_or_risk"
    ARCHITECTURE = "architecture"
    DEPENDENCY = "dependency"


class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Finding(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    title: str = Field(min_length=1)
    description: str = Field(min_length=1)
    category: FindingCategory
    confidence: float = Field(ge=0.0, le=1.0)
    evidence_ids: list[str] = Field(default_factory=list)


class RecoveryAction(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    title: str = Field(min_length=1)
    description: str = Field(min_length=1)
    priority: Priority
    reason: str = Field(min_length=1)
    evidence_ids: list[str] = Field(default_factory=list)