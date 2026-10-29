import logging
from pathlib import Path
from typing import Optional

from ghost_projects.types.assessment import ProjectAssessment
from ghost_projects.types.report import RecoveryReport, ReportFormat
from ghost_projects.types.finding import Priority

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
        lines.append("# Project Recovery Report")
        lines.append(f"\n## 1. Project Overview")
        lines.append(f"**Purpose:** {assessment.purpose}")
        lines.append(f"\n**Summary:**\n{assessment.summary}")
        
        lines.append(f"\n## 2. Architecture Reconstruction")
        lines.append(assessment.architecture)
        
        # Findings
        lines.append(f"\n## 3. Key Findings")
        if not assessment.findings:
            lines.append("No specific findings were identified.")
        else:
            for i, finding in enumerate(assessment.findings, 1):
                lines.append(f"\n### Finding {i}: {finding.title}")
                lines.append(f"- **Category:** {finding.category.value}")
                lines.append(f"- **Confidence:** {finding.confidence:.2%}")
                lines.append(f"\n**Description:**\n{finding.description}")
                
                if finding.evidence_ids:
                    lines.append("\n**Supporting Evidence:**")
                    for ev_id in finding.evidence_ids:
                        ev = next((e for e in assessment.evidence if e.id == ev_id), None)
                        if ev:
                            lines.append(f"- `{ev.id}`: {ev.description} (Path: `{ev.source_path}`)")
                            if ev.excerpt:
                                lines.append(f"  > {ev.excerpt}")
                                if ev.line_start:
                                    lines.append(f"  *(Lines {ev.line_start}-{ev.line_end or ev.line_start})*")
                        else:
                            lines.append(f"- `{ev_id}`: [Evidence missing from assessment]")

        # Recovery Plan
        lines.append(f"\n## 4. Recovery Plan")
        if not assessment.recovery_plan:
            lines.append("No specific recovery actions were identified.")
        else:
            # Sort by priority: HIGH -> MEDIUM -> LOW
            priority_map = {Priority.HIGH: 0, Priority.MEDIUM: 1, Priority.LOW: 2}
            sorted_actions = sorted(
                assessment.recovery_plan, 
                key=lambda x: priority_map.get(x.priority, 3)
            )
            
            for i, action in enumerate(sorted_actions, 1):
                lines.append(f"\n### Action {i}: {action.title}")
                lines.append(f"- **Priority:** {action.priority.value.upper()}")
                lines.append(f"\n**Reasoning:**\n{action.reason}")
                lines.append(f"\n**Proposed Action:**\n{action.description}")
                
                if action.evidence_ids:
                    lines.append("\n**Supporting Evidence:**")
                    for ev_id in action.evidence_ids:
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