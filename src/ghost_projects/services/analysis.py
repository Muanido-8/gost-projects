import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from ghost_projects.schemas.analysis import AnalysisResult, AnalysisStatus
from ghost_projects.schemas.project import ProjectInfo
from ghost_projects.services.scanner import ProjectScanner
from ghost_projects.services.reader import FileReader
from ghost_projects.services.detector import ProjectDetector
from ghost_projects.services.git_inspector import GitInspector
from ghost_projects.services.evidence import EvidenceCollector
from ghost_projects.services.file_filter import FileFilter

logger = logging.getLogger(__name__)

class AnalysisService:
    """
    Orchestrates the repository inspection process by coordinating other services.
    """

    def __init__(
        self,
        scanner: Optional[ProjectScanner] = None,
        reader: Optional[FileReader] = None,
        detector: Optional[ProjectDetector] = None,
        git_inspector: Optional[GitInspector] = None,
        evidence_collector: Optional[EvidenceCollector] = None,
    ):
        self.scanner = scanner or ProjectScanner()
        self.reader = reader or FileReader()
        self.detector = detector or ProjectDetector()
        self.git_inspector = git_inspector or GitInspector()
        self.evidence_collector = evidence_collector or EvidenceCollector()

    def run_analysis(self, root: Path) -> AnalysisResult:
        """
        Performs a full repository inspection.
        
        Args:
            root: The root directory of the project to analyze.
            
        Returns:
            An AnalysisResult containing the gathered project information.
        """
        # Define filter
        filter = FileFilter(root)
        self.reader = FileReader(file_filter=filter)

        result = AnalysisResult(
            project=ProjectInfo(name=root.name, root_path=root, detected_languages=[], detected_technologies=[], has_git=False),
            status=AnalysisStatus.SCANNING
        )

        try:
            # 1. Scan Project Files
            logger.info(f"Scanning project at {root}...")
            all_files = list(self.scanner.scan(root))
            file_paths = [f.path for f in all_files]

            # 2. Detect Technologies
            logger.info("Detecting technologies...")
            project_info = self.detector.detect(root, file_paths)
            result.project = project_info

            # 3. Inspect Git History
            if project_info.has_git:
                logger.info("Inspecting Git history...")
                git_history = self.git_inspector.get_history(root)
                if git_history:
                    # We could add git history to the result if AnalysisResult had a field for it,
                    # but based on types/analysis.py, it only has ProjectInfo and ProjectAssessment.
                    # We'll log the success.
                    logger.info(f"Collected {git_history.total_commits} commits.")
                else:
                    result.warnings.append("Git repository detected but history could not be retrieved.")
            
            # 4. Initial Evidence Collection (e.g., README)
            self._collect_initial_evidence(file_paths)

            result.status = AnalysisStatus.COMPLETED
            result.finished_at = datetime.now(timezone.utc)

        except (FileNotFoundError, NotADirectoryError) as e:
            logger.error(f"Fatal error during analysis: {e}")
            result.status = AnalysisStatus.FAILED
            result.errors.append(str(e))
            result.finished_at = datetime.now(timezone.utc)
        except Exception as e:
            logger.exception(f"Unexpected error during analysis: {e}")
            result.status = AnalysisStatus.FAILED
            result.errors.append(f"Unexpected error: {str(e)}")
            result.finished_at = datetime.now(timezone.utc)

        return result

    def _collect_initial_evidence(self, file_paths: list[Path]):
        """
        Collects basic evidence from key files like README.md.
        """
        for path in file_paths:
            if path.name.lower() == "readme.md":
                content_res = self.reader.read_file(path)
                if not isinstance(content_res, (Exception, object)) or hasattr(content_res, 'content'):
                    # This is a simplified check since we know the types
                    # In a real scenario, we'd check if it's FileContent
                    try:
                        # We assume it's FileContent if it has content
                        excerpt = getattr(content_res, 'content', "")[:500]
                        self.evidence_collector.create_evidence(
                            source_path=str(path),
                            description="Project README content",
                            excerpt=excerpt
                        )
                    except Exception:
                        pass