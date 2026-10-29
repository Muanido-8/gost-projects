import logging
from pathlib import Path
from typing import Generator, Set

from ghost_projects.config.settings import settings
from ghost_projects.types.file import ProjectFile

logger = logging.getLogger(__name__)

class ProjectScanner:
    """
    Responsible for discovering files and directories inside a user-selected project.
    """

    DEFAULT_EXCLUDED_DIRS: Set[str] = {
        ".git",
        ".venv",
        "venv",
        "node_modules",
        "__pycache__",
        "build",
        "dist",
        ".idea",
        ".vscode",
        "target",
    }

    def __init__(self, excluded_dirs: set[str] | None = None):
        self.excluded_dirs = excluded_dirs if excluded_dirs is not None else self.DEFAULT_EXCLUDED_DIRS

    def is_ignored(self, path: Path) -> bool:
        """
        Check if a path should be ignored based on the excluded directories list.
        """
        return any(part in self.excluded_dirs for part in path.parts)

    def scan(self, root: Path) -> Generator[ProjectFile, None, None]:
        """
        Recursively discover relevant files inside the project root.
        
        Args:
            root: The root directory of the project to scan.
            
        Yields:
            ProjectFile objects for each discovered file.
            
        Raises:
            FileNotFoundError: If the root path does not exist.
            NotADirectoryError: If the root path is not a directory.
        """
        if not root.exists():
            raise FileNotFoundError(f"Project root not found: {root}")
        if not root.is_dir():
            raise NotADirectoryError(f"Project root is not a directory: {root}")

        files_found = 0
        
        try:
            # Use rglob('*') for recursive discovery
            # We sort the results to ensure deterministic scanning
            for path in sorted(root.rglob("*")):
                if files_found >= settings.max_files_per_scan:
                    logger.warning("Maximum file count reached. Stopping scan.")
                    break

                if self.is_ignored(path):
                    continue

                # Avoid following directory symlinks by default
                if path.is_symlink() and path.is_dir():
                    continue

                try:
                    if path.is_file():
                        # Respect maximum file size
                        size = path.stat().st_size
                        if size > settings.max_file_size_bytes:
                            # We still record the file but it might be skipped by the reader
                            # Or we can choose to skip it here. The requirements say 
                            # "Respect configured limits", usually meaning don't process 
                            # huge files. I'll include it in the scan but the reader 
                            # will handle the size limit for content.
                            pass
                        
                        yield ProjectFile(
                            path=path,
                            name=path.name,
                            extension=path.suffix,
                            size_bytes=size,
                            is_directory=False
                        )
                        files_found += 1
                    elif path.is_dir():
                        # We can also yield directories if needed, but ProjectFile 
                        # is typically for files. The type has is_directory.
                        yield ProjectFile(
                            path=path,
                            name=path.name,
                            extension="",
                            size_bytes=0,
                            is_directory=True
                        )
                        # Directories don't count towards max_files_per_scan usually,
                        # but let's be consistent.
                except (PermissionError, OSError) as e:
                    logger.error(f"Error accessing {path}: {e}")
                    continue

        except Exception as e:
            logger.exception(f"Unexpected error during project scan: {e}")
            raise