
import logging
import os
from pathlib import Path
from typing import Generator, Set

from ghost_projects.config.settings import settings
from ghost_projects.schemas.file import ProjectFile
from ghost_projects.services.file_filter import FileFilter

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
        self.excluded_dirs = (
            excluded_dirs
            if excluded_dirs is not None
            else self.DEFAULT_EXCLUDED_DIRS
        )
        self.file_filter: FileFilter | None = None

    def is_ignored(self, path: Path) -> bool:
        """
        Check if a path should be ignored based on excluded directories
        and configured .ghostignore rules.
        """

        if any(part in self.excluded_dirs for part in path.parts):
            return True

        if self.file_filter and not self.file_filter.is_allowed(path):
            return True

        return False

    def scan(self, root: Path) -> Generator[ProjectFile, None, None]:
        """
        Recursively discover relevant files and directories inside the project root.

        Args:
            root: The root directory of the project to scan.

        Yields:
            ProjectFile objects for each discovered file or directory.

        Raises:
            FileNotFoundError: If the root path does not exist.
            NotADirectoryError: If the root path is not a directory.
        """

        if not root.exists():
            raise FileNotFoundError(f"Project root not found: {root}")

        if not root.is_dir():
            raise NotADirectoryError(f"Project root is not a directory: {root}")

        root = root.resolve()
        self.file_filter = FileFilter(project_root=root)

        files_found = 0

        try:
            for current_root, dirs, files in os.walk(
                root,
                topdown=True,
                followlinks=False,
                onerror=lambda error: logger.error(
                    f"Error accessing directory: {error}"
                ),
            ):
                current_path = Path(current_root)

                # Filter directories before traversal.
                dirs[:] = sorted(
                    directory
                    for directory in dirs
                    if not self.is_ignored(current_path / directory)
                    and not (current_path / directory).is_symlink()
                )

                # Yield directories, preserving the previous behavior.
                for directory in dirs:
                    path = current_path / directory

                    yield ProjectFile(
                        path=path,
                        name=path.name,
                        extension="",
                        size_bytes=0,
                        is_directory=True,
                    )

                # Process files deterministically.
                for filename in sorted(files):
                    if files_found >= settings.max_files_per_scan:
                        logger.warning(
                            "Maximum file count reached. Stopping scan."
                        )
                        return

                    path = current_path / filename

                    if self.is_ignored(path):
                        continue

                    # Do not follow file symlinks.
                    if path.is_symlink():
                        continue

                    try:
                        if not path.is_file():
                            continue

                        size = path.stat().st_size

                        yield ProjectFile(
                            path=path,
                            name=path.name,
                            extension=path.suffix,
                            size_bytes=size,
                            is_directory=False,
                        )

                        files_found += 1

                    except (PermissionError, OSError) as e:
                        logger.error(f"Error accessing {path}: {e}")
                        continue

        except Exception as e:
            logger.exception(
                f"Unexpected error during project scan: {e}"
            )
            raise
