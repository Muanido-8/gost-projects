
from pathlib import Path
from collections.abc import Iterable

from pathspec import GitIgnoreSpec


class FileFilter:
    """
    Filters project files using:
    - Internal Ghost Projects ignore rules.
    - Optional user-defined .ghostignore at project root.

    Internal rules always take precedence.
    """

    def __init__(self, project_root: Path):
        self.project_root = Path(project_root).resolve()

        internal_ignore = (
            Path(__file__).resolve().parents[1]
            / "resources"
            / ".ghostignore"
        )

        self.internal_spec = self._load_spec(internal_ignore)

        user_ignore = self.project_root / ".ghostignore"
        self.user_spec = self._load_spec(user_ignore)

    @staticmethod
    def _load_spec(file_path: Path) -> GitIgnoreSpec:
        """Load GitIgnore-compatible patterns from a file."""

        if not file_path.is_file():
            return GitIgnoreSpec.from_lines([])

        lines = file_path.read_text(encoding="utf-8").splitlines()

        return GitIgnoreSpec.from_lines(lines)

    def _get_relative_path(self, path: Path | str) -> str | None:
        """
        Resolve a path and return its project-relative representation.
        Returns None if the path is outside the project.
        """

        path = Path(path)

        if not path.is_absolute():
            path = self.project_root / path

        try:
            resolved = path.resolve()
            relative = resolved.relative_to(self.project_root)
            return relative.as_posix()

        except (ValueError, OSError):
            return None

    def is_allowed(self, path: Path | str) -> bool:
        """Return True if the file is allowed to be analyzed."""

        relative_path = self._get_relative_path(path)

        # Reject paths outside the inspected project.
        if relative_path is None:
            return False

        # Internal rules cannot be overridden.
        if self.internal_spec.match_file(relative_path):
            return False

        # Apply user-defined rules.
        if self.user_spec.match_file(relative_path):
            return False

        return True

    def filter_paths(
        self,
        paths: Iterable[Path | str],
    ) -> list[Path]:
        """Return a new list containing only allowed paths."""

        return [
            Path(path)
            for path in paths
            if self.is_allowed(path)
        ]
