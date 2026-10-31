from pydantic import BaseModel, ConfigDict, Field, model_validator

from ghost_projects.schemas.evidence import Evidence
from ghost_projects.schemas.finding import Clue, ResurrectionStep


class ProjectAssessment(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    original_intent: str = Field(min_length=1, description="The original purpose and goal of the project as deduced from the investigation.")
    investigation_summary: str = Field(min_length=1, description="A comprehensive summary of the project's current state and the investigator's findings.")
    recovered_architecture: str = Field(min_length=1, description="A detailed description of the project's architecture to help the user understand how it was built.")

    clues: list[Clue] = Field(default_factory=list, description="Clues found during the investigation that point to the project's state and history.")
    evidence: list[Evidence] = Field(default_factory=list)
    resurrection_plan: list[ResurrectionStep] = Field(default_factory=list, description="A concrete, step-by-step plan to bring the project back to life.")
    unknowns: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_evidence_references(self) -> "ProjectAssessment":
        evidence_ids = [item.id for item in self.evidence]

        if len(evidence_ids) != len(set(evidence_ids)):
            raise ValueError("Evidence IDs must be unique")

        known_ids = set(evidence_ids)

        for clue in self.clues:
            missing = set(clue.evidence_ids) - known_ids
            if missing:
                raise ValueError(
                    f"Clue '{clue.title}' references "
                    f"unknown evidence IDs: {sorted(missing)}"
                )

        for step in self.resurrection_plan:
            missing = set(step.evidence_ids) - known_ids
            if missing:
                raise ValueError(
                    f"Resurrection step '{step.title}' references "
                    f"unknown evidence IDs: {sorted(missing)}"
                )

        return self