from pathlib import Path

import pytest
from pydantic import ValidationError

from ghost_projects.types import (
    Evidence,
    Finding,
    FindingCategory,
    Priority,
    ProjectAssessment,
    ProjectInfo,
    RecoveryAction,
)


def test_project_info() -> None:
    project = ProjectInfo(
        name="example",
        root_path=Path("/tmp/example"),
        detected_languages=["Python"],
        has_git=True,
    )

    assert project.name == "example"
    assert project.has_git is True


def test_finding_rejects_invalid_confidence() -> None:
    with pytest.raises(ValidationError):
        Finding(
            title="Incomplete feature",
            description="A feature appears unfinished.",
            category=FindingCategory.INCOMPLETE_FEATURE,
            confidence=1.5,
            evidence_ids=[],
        )


def test_assessment_rejects_unknown_evidence() -> None:
    finding = Finding(
        title="Incomplete feature",
        description="A feature appears unfinished.",
        category=FindingCategory.INCOMPLETE_FEATURE,
        confidence=0.8,
        evidence_ids=["E999"],
    )

    with pytest.raises(ValidationError):
        ProjectAssessment(
            purpose="Example project",
            summary="An example assessment",
            architecture="Unknown",
            findings=[finding],
            evidence=[],
        )


def test_assessment_accepts_valid_evidence() -> None:
    evidence = Evidence(
        id="E001",
        source_path=Path("src/main.py"),
        description="A TODO comment exists.",
        excerpt="# TODO: implement authentication",
        line_start=10,
        line_end=10,
    )

    finding = Finding(
        title="Authentication may be incomplete",
        description="A TODO suggests unfinished authentication work.",
        category=FindingCategory.INCOMPLETE_FEATURE,
        confidence=0.8,
        evidence_ids=["E001"],
    )

    action = RecoveryAction(
        title="Investigate authentication",
        description="Inspect the authentication implementation.",
        priority=Priority.HIGH,
        reason="The source contains an unresolved TODO.",
        evidence_ids=["E001"],
    )

    assessment = ProjectAssessment(
        purpose="Example application",
        summary="An application under investigation.",
        architecture="Python application",
        findings=[finding],
        evidence=[evidence],
        recovery_plan=[action],
    )

    assert assessment.findings[0].evidence_ids == ["E001"]
    assert assessment.recovery_plan[0].priority == Priority.HIGH