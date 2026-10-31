
import logging
from pathlib import Path
from typing import Sequence, Union

from ghost_projects.config.settings import settings
from ghost_projects.schemas.file import FileContent, FileReadError
from ghost_projects.services.file_filter import FileFilter

logger = logging.getLogger(__name__)


class FileReader:
    """
    Responsible for reading relevant textual files discovered by the scanner.
    """

    def __init__(self, file_filter: FileFilter | None = None):
        self.max_size = settings.max_file_size_bytes
        self.max_chars = settings.max_file_content_chars
        self.file_filter = file_filter

    def is_binary(self, path: Path) -> bool:
        """
        Heuristic to check if a file is binary.
        Reads the first 1024 bytes and checks for null bytes.
        """
        try:
            with open(path, "rb") as f:
                chunk = f.read(1024)
                return b"\x00" in chunk
        except Exception:
            return True

    def read_file(self, path: Path) -> Union[FileContent, FileReadError]:
        """
        Reads a single file and returns its content or an error.
        """
        try:
            # Require a configured filter before accessing files.
            if self.file_filter is None:
                return FileReadError(
                    path=path,
                    reason="File filter is not configured"
                )

            # Apply ignore rules before accessing the file.
            if not self.file_filter.is_allowed(path):
                return FileReadError(
                    path=path,
                    reason="File is excluded by project ignore rules"
                )

            if path.is_symlink():
                return FileReadError(
                    path=path,
                    reason="Symbolic links are not allowed"
                )

            if not path.exists():
                return FileReadError(
                    path=path,
                    reason="File not found"
                )

            if not path.is_file():
                return FileReadError(
                    path=path,
                    reason="Path is not a file"
                )

            # Respect maximum file size before reading.
            size = path.stat().st_size

            if size > self.max_size:
                return FileReadError(
                    path=path,
                    reason=f"File size {size} exceeds limit {self.max_size}"
                )

            if self.is_binary(path):
                return FileReadError(
                    path=path,
                    reason="Binary file detected"
                )

            # Read content with encoding handling.
            # Try UTF-8 first, then fallback to Latin-1.
            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
            except UnicodeDecodeError:
                with open(path, "r", encoding="latin-1") as f:
                    content = f.read()

            truncated = False

            if len(content) > self.max_chars:
                content = content[:self.max_chars]
                truncated = True

            return FileContent(
                path=path,
                content=content,
                truncated=truncated
            )

        except PermissionError:
            return FileReadError(
                path=path,
                reason="Permission denied"
            )

        except Exception as e:
            logger.error(f"Unexpected error reading {path}: {e}")

            return FileReadError(
                path=path,
                reason=str(e)
            )

    def read_batch(
        self,
        paths: Sequence[Path]
    ) -> Sequence[Union[FileContent, FileReadError]]:
        """
        Reads multiple files in batch.
        """
        results = []

        for path in paths:
            results.append(self.read_file(path))

        return results
