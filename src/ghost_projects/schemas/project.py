from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field


class ProjectInfo(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    name: str = Field(min_length=1)
    root_path: Path
    detected_languages: list[str] = Field(default_factory=list)
    detected_technologies: list[str] = Field(default_factory=list)
    has_git: bool = False