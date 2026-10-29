from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field


class ProjectFile(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    path: Path
    name: str = Field(min_length=1)
    extension: str = ""
    size_bytes: int = Field(ge=0)
    is_directory: bool = False


class FileContent(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    path: Path
    content: str
    truncated: bool = False


class FileReadError(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    path: Path
    reason: str = Field(min_length=1)