from pydantic import BaseModel, ConfigDict, Field, model_validator

from ghost_projects.types.evidence import Evidence
from ghost_projects.types.finding import Finding, RecoveryAction


class ProjectAssessment(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    purpose: str = Field(min_length=1)
    summary: str = Field(min_length=1)
    architecture: str = Field(min_length=1)

    findings: list[Finding] = Field(default_factory=list)
    evidence: list[Evidence] = Field(default_factory=list)
    recovery_plan: list[RecoveryAction] = Field(default_factory=list)
    unknowns: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_evidence_references(self) -> "ProjectAssessment":
        evidence_ids = [item.id for item in self.evidence]

        if len(evidence_ids) != len(set(evidence_ids)):
            raise ValueError("Evidence IDs must be unique")

        known_ids = set(evidence_ids)

        for finding in self.findings:
            missing = set(finding.evidence_ids) - known_ids
            if missing:
                raise ValueError(
                    f"Finding '{finding.title}' references "
                    f"unknown evidence IDs: {sorted(missing)}"
                )

        for action in self.recovery_plan:
            missing = set(action.evidence_ids) - known_ids
            if missing:
                raise ValueError(
                    f"Recovery action '{action.title}' references "
                    f"unknown evidence IDs: {sorted(missing)}"
                )

        return self