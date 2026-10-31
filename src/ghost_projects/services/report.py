import logging
from pathlib import Path
from typing import Optional

from ghost_projects.schemas.assessment import ProjectAssessment
from ghost_projects.schemas.report import RecoveryReport, ReportFormat
from ghost_projects.schemas.finding import Priority

logger = logging.getLogger(__name__)

class ReportService:
    """
    Responsible for converting a completed assessment into a readable Markdown recovery report.
    """

    def generate_markdown(self, assessment: ProjectAssessment) -> str:
        """
        Generates a professional Markdown report from a project assessment.
        """
        lines = []
        
        # Title and Header
        lines.append("# Project Resurrection Report")
        lines.append(f"\n## 1. Project Overview")
        lines.append(f"**Original Intent:** {assessment.original_intent}")
        lines.append(f"\n**Investigation Summary:**\n{assessment.investigation_summary}")
        
        lines.append(f"\n## 2. Recovered Architecture")
        lines.append(assessment.recovered_architecture)
        
        # Clues
        lines.append(f"\n## 3. Investigation Clues")
        if not assessment.clues:
            lines.append("No specific clues were identified.")
        else:
            for i, clue in enumerate(assessment.clues, 1):
                lines.append(f"\n### Clue {i}: {clue.title}")
                lines.append(f"- **Category:** {clue.category.value}")
                lines.append(f"- **Confidence:** {clue.confidence:.2%}")
                lines.append(f"\n**Description:**\n{clue.description}")
                
                if clue.evidence_ids:
                    lines.append("\n**Supporting Evidence:**")
                    for ev_id in clue.evidence_ids:
                        ev = next((e for e in assessment.evidence if e.id == ev_id), None)
                        if ev:
                            lines.append(f"- `{ev.id}`: {ev.description} (Path: `{ev.source_path}`)")
                            if ev.excerpt:
                                lines.append(f"  > {ev.excerpt}")
                                if ev.line_start:
                                    lines.append(f"  *(Lines {ev.line_start}-{ev.line_end or ev.line_start})*")
                        else:
                            lines.append(f"- `{ev_id}`: [Evidence missing from assessment]")

        # Resurrection Plan
        lines.append(f"\n## 4. Resurrection Plan")
        if not assessment.resurrection_plan:
            lines.append("No specific resurrection steps were identified. The project may be beyond recovery.")
        else:
            # Sort by priority: HIGH -> MEDIUM -> LOW
            priority_map = {Priority.HIGH: 0, Priority.MEDIUM: 1, Priority.LOW: 2}
            sorted_steps = sorted(
                assessment.resurrection_plan, 
                key=lambda x: priority_map.get(x.priority, 3)
            )
            
            for i, step in enumerate(sorted_steps, 1):
                lines.append(f"\n### Step {i}: {step.title}")
                lines.append(f"- **Priority:** {step.priority.value.upper()}")
                lines.append(f"\n**Concrete Action:**\n{step.concrete_action}")
                lines.append(f"\n**Details:**\n{step.description}")
                
                if step.evidence_ids:
                    lines.append("\n**Supporting Evidence:**")
                    for ev_id in step.evidence_ids:
                        ev = next((e for e in assessment.evidence if e.id == ev_id), None)
                        if ev:
                            lines.append(f"- `{ev.id}`: {ev.description}")
                        else:
                            lines.append(f"- `{ev_id}`: [Evidence missing]")

        # Unknowns and Limitations
        lines.append(f"\n## 5. Unknowns and Limitations")
        if not assessment.unknowns:
            lines.append("No significant unknowns were identified.")
        else:
            for unknown in assessment.unknowns:
                lines.append(f"- {unknown}")

        return "\n".join(lines)

    def save_report(self, assessment: ProjectAssessment, destination: Path) -> Optional[RecoveryReport]:
        """
        Generates and saves the recovery report to the specified destination.
        
        Args:
            assessment: The completed project assessment.
            destination: The path where the report should be saved.
            
        Returns:
            A RecoveryReport object if successful, None otherwise.
        """
        try:
            if destination.exists():
                logger.warning(f"Report destination {destination} already exists. Skipping to avoid overwrite.")
                return None

            markdown_content = self.generate_markdown(assessment)
            
            # Ensure parent directory exists
            destination.parent.mkdir(parents=True, exist_ok=True)
            
            destination.write_text(markdown_content, encoding="utf-8")
            
            return RecoveryReport(
                assessment=assessment,
                format=ReportFormat.MARKDOWN
            )

        except Exception as e:
            logger.error(f"Failed to save report to {destination}: {e}")
            return None