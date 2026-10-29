import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Generator, Optional

from ghost_projects.config.settings import settings

logger = logging.getLogger(__name__)

@dataclass(frozen=True)
class SearchOptions:
    """
    Configuration options for the file search service.
    """
    query: str
    use_regex: bool = False
    case_sensitive: bool = False
    include_patterns: list[str] = field(default_factory=list)
    exclude_patterns: list[str] = field(default_factory=list)
    extensions: list[str] = field(default_factory=list)
    max_results: int = 1000
    context_lines: int = 1

@dataclass(frozen=True)
class SearchMatch:
    """
    A single match found in a file.
    """
    path: Path
    line_number: int
    matched_text: str
    context: str

class SearchError(Exception):
    """Base exception for search operations."""
    pass

class InvalidRegexError(SearchError):
    """Raised when a provided regular expression is invalid."""
    def __init__(self, pattern: str, details: str):
        super().__init__(f"Invalid regular expression '{pattern}': {details}")
        self.pattern = pattern
        self.details = details

class FileSearchService:
    """
    Provides 'Find in Files' functionality across the project.
    """

    def search(self, root: Path, options: SearchOptions) -> Generator[SearchMatch, None, None]:
        """
        Searches for the query across files in the project root.
        
        Args:
            root: The project root directory.
            options: Search configuration options.
            
        Yields:
            SearchMatch objects for each occurrence found.
            
        Raises:
            InvalidRegexError: If the regex pattern is invalid.
        """
        pattern = self._compile_pattern(options)
        results_count = 0

        # Discover files to search
        for path in root.rglob("*"):
            if results_count >= options.max_results:
                break

            if not path.is_file():
                continue

            if not self._should_search_file(path, options):
                continue

            # Avoid following directory symlinks (already handled by is_file, 
            # but we check for safety)
            if path.is_symlink():
                continue

            # Respect file size limit from settings
            try:
                if path.stat().st_size > settings.max_file_size_bytes:
                    continue
            except OSError:
                continue

            # Search the file line by line
            try:
                for match in self._search_in_file(path, pattern, options):
                    yield match
                    results_count += 1
                    if results_count >= options.max_results:
                        break
            except (UnicodeDecodeError, PermissionError) as e:
                logger.debug(f"Skipping file {path} due to read error: {e}")
                continue

    def _compile_pattern(self, options: SearchOptions) -> re.Pattern:
        """Compiles the search query into a regex pattern."""
        flags = 0
        if not options.case_sensitive:
            flags |= re.IGNORECASE

        if options.use_regex:
            try:
                return re.compile(options.query, flags)
            except re.error as e:
                raise InvalidRegexError(options.query, str(e))
        else:
            # Escape literal text for regex
            return re.compile(re.escape(options.query), flags)

    def _should_search_file(self, path: Path, options: SearchOptions) -> bool:
        """Determines if a file should be included in the search based on options."""
        # Check extensions
        if options.extensions and path.suffix not in options.extensions:
            return False

        # Check exclude patterns (glob)
        for pattern in options.exclude_patterns:
            if path.match(pattern):
                return False

        # Check include patterns (glob)
        if options.include_patterns:
            if not any(path.match(pattern) for pattern in options.include_patterns):
                return False

        return True

    def _search_in_file(self, path: Path, pattern: re.Pattern, options: SearchOptions) -> Generator[SearchMatch, None, None]:
        """Searches for the pattern within a single file."""
        # Use a buffer to keep track of lines for context
        lines = []
        
        # We read the file line by line to be memory efficient
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            for i, line in enumerate(f, 1):
                lines.append(line)
                if len(lines) > options.context_lines + 1:
                    lines.pop(0)

                if pattern.search(line):
                    # Extract matched text
                    match_obj = pattern.search(line)
                    matched_text = match_obj.group(0)
                    
                    # Build context
                    context_start = max(0, len(lines) - 1 - options.context_lines)
                    context_lines = lines[context_start:-1] if options.context_lines > 0 else []
                    context = "\n".join(context_lines).strip()

                    yield SearchMatch(
                        path=path,
                        line_number=i,
                        matched_text=matched_text,
                        context=context
                    )