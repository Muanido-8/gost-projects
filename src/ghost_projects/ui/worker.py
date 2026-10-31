import asyncio
import logging
from pathlib import Path
from PySide6.QtCore import QObject, Signal, Slot

from ghost_projects.schemas.project import ProjectInfo
from ghost_projects.services.scanner import ProjectScanner
from ghost_projects.services.reader import FileReader
from ghost_projects.services.search import FileSearchService
from ghost_projects.services.git_inspector import GitInspector
from ghost_projects.services.evidence import EvidenceCollector
from ghost_projects.services.file_filter import FileFilter
from ghost_projects.ai.runner import run_investigation

logger = logging.getLogger(__name__)

class InvestigationWorker(QObject):
    finished = Signal(str)  # Result text
    error = Signal(str)     # Error message
    status = Signal(str)    # Current status message

    def __init__(self, project_path: Path):
        super().__init__()
        self.project_path = project_path
        self._is_cancelled = False

    @Slot()
    def run(self):
        """Entry point for the worker thread."""
        try:
            # Run the async investigation in a new event loop
            result_text = asyncio.run(self._execute_investigation())
            self.finished.emit(result_text)
        except Exception as e:
            logger.exception("Worker failed during investigation")
            self.error.emit(str(e))

    async def _execute_investigation(self) -> str:
        # Atmospheric status messages
        status_messages = [
            "Awakening the forgotten...",
            "Examining digital remains...",
            "Searching for lost memories...",
            "Reconstructing the project's past...",
            "Consulting the digital oracle...",
            "Sifting through ghost code..."
        ]
        
        # We can't easily "stream" status from the current run_investigation 
        # without modifying it, so we'll emit a few initial ones.
        for msg in status_messages[:3]:
            self.status.emit(msg)
            await asyncio.sleep(1)

        # 1. Initialization of Services (as per test.py)
        self.status.emit("Initializing services...")
        scanner = ProjectScanner()
        file_filter = FileFilter(self.project_path)
        reader = FileReader(file_filter=file_filter)
        search_service = FileSearchService()
        git_inspector = GitInspector()
        evidence_collector = EvidenceCollector()

        # 2. Project Info
        has_git = git_inspector.is_git_repository(self.project_path)
        project_info = ProjectInfo(
            name=self.project_path.name,
            root_path=self.project_path,
            detected_languages=[],
            detected_technologies=[],
            has_git=has_git
        )

        self.status.emit("Executing deep investigation...")
        
        # 3. Run Investigation
        assessment = await run_investigation(
            project_info=project_info,
            scanner=scanner,
            reader=reader,
            search_service=search_service,
            git_inspector=git_inspector,
            evidence_collector=evidence_collector,
            max_turns=19
        )

        # 4. Format Result as Plain Text
        return self._format_assessment(assessment, has_git)

    def _format_assessment(self, assessment, has_git: bool) -> str:
        lines = []
        lines.append("="*80)
        lines.append(f" GHOST PROJECT ASSESSMENT: {assessment.original_intent if hasattr(assessment, 'original_intent') else 'Unknown'}")
        lines.append("="*80)
        
        lines.append(f"\n[OVERVIEW]\n{assessment.investigation_summary}")
        lines.append(f"\n[ARCHITECTURE]\n{assessment.recovered_architecture}")
        lines.append(f"\n[GIT DETECTED]: {'Yes' if has_git else 'No'}")

        if assessment.clues:
            lines.append("\n" + "-"*30)
            lines.append("[CLUES FOUND]")
            lines.append("-"*30)
            for i, clue in enumerate(assessment.clues, 1):
                lines.append(f"{i}. {clue.title} ({clue.category.value})")
                lines.append(f"   Confidence: {clue.confidence:.2%}")
                lines.append(f"   Description: {clue.description}")
                lines.append("")

        if assessment.resurrection_plan:
            lines.append("\n" + "-"*30)
            lines.append("[RESURRECTION PLAN]")
            lines.append("-"*30)
            for i, step in enumerate(assessment.resurrection_plan, 1):
                lines.append(f"{i}. {step.title} [Priority: {step.priority.value.upper()}]")
                lines.append(f"   Action: {step.concrete_action}")
                lines.append(f"   Details: {step.description}")
                lines.append("")

        if assessment.evidence:
            lines.append("\n" + "-"*30)
            lines.append("[COLLECTED EVIDENCE]")
            lines.append("-"*30)
            for ev in assessment.evidence:
                lines.append(f"ID: {ev.id} | File: {ev.source_path}")
                lines.append(f"Description: {ev.description}")
                if ev.excerpt:
                    lines.append(f"Excerpt:\n---\n{ev.excerpt}\n---")
                lines.append("")

        if assessment.unknowns:
            lines.append("\n" + "-"*30)
            lines.append("[GHOSTS & LIMITATIONS]")
            lines.append("-"*30)
            for unknown in assessment.unknowns:
                lines.append(f"- {unknown}")

        return "\n".join(lines)