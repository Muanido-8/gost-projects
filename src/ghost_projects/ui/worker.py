import asyncio
import logging
from pathlib import Path
from PySide6.QtCore import QObject, Signal, Slot

from ghost_projects.schemas.project import ProjectInfo
from ghost_projects.schemas.assessment import ProjectAssessment
from ghost_projects.services.scanner import ProjectScanner
from ghost_projects.services.reader import FileReader
from ghost_projects.services.search import FileSearchService
from ghost_projects.services.git_inspector import GitInspector
from ghost_projects.services.evidence import EvidenceCollector
from ghost_projects.services.file_filter import FileFilter
from ghost_projects.ai.runner import run_investigation

logger = logging.getLogger(__name__)

class InvestigationWorker(QObject):
    finished = Signal(object, object)  # (ProjectInfo, ProjectAssessment)
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
            project_info, assessment = asyncio.run(self._execute_investigation())
            self.finished.emit(project_info, assessment)
        except Exception as e:
            logger.exception("Worker failed during investigation")
            self.error.emit(str(e))

    async def _execute_investigation(self) -> tuple[ProjectInfo, ProjectAssessment]:
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

        return project_info, assessment
