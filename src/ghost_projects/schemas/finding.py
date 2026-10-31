from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class ClueCategory(str, Enum):
    ORIGINAL_INTENT = "original_intent"
    LEGACY_CODE = "legacy_code"
    ABANDONED_FEATURE = "abandoned_feature"
    ARCHITECTURAL_REMNANT = "architectural_remnant"
    DEPENDENCY_GHOST = "dependency_ghost"
    SETUP_ARTIFACT = "setup_artifact"


class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Clue(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    title: str = Field(min_length=1)
    description: str = Field(min_length=1)
    category: ClueCategory
    confidence: float = Field(ge=0.0, le=1.0)
    evidence_ids: list[str] = Field(default_factory=list)


class ResurrectionStep(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    title: str = Field(min_length=1)
    description: str = Field(min_length=1)
    priority: Priority
    concrete_action: str = Field(min_length=1, description="A specific, actionable step the user must take to recover the project.")
    evidence_ids: list[str] = Field(default_factory=list)
