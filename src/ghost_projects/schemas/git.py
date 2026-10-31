from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class GitCommit(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    hash: str = Field(min_length=1)
    message: str
    committed_at: datetime
    changed_files: list[str] = Field(default_factory=list)


class GitHistory(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    commits: list[GitCommit] = Field(default_factory=list)
    total_commits: int = Field(ge=0)