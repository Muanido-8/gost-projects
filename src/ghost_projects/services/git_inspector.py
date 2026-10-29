import logging
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from ghost_projects.types.git import GitCommit, GitHistory

logger = logging.getLogger(__name__)

class GitInspector:
    """
    Responsible for inspecting Git history when the selected project contains a repository.
    """

    def __init__(self, max_commits: int = 100):
        self.max_commits = max_commits

    def is_git_repository(self, root: Path) -> bool:
        """
        Checks if the given root directory is a Git repository.
        """
        return (root / ".git").exists() and (root / ".git").is_dir()

    def get_history(self, root: Path) -> Optional[GitHistory]:
        """
        Collects commit history from the Git repository.
        
        Args:
            root: The root directory of the project.
            
        Returns:
            A GitHistory object if successful, None otherwise.
        """
        if not self.is_git_repository(root):
            return None

        try:
            # Format: hash|timestamp|subject
            # %H: commit hash, %ct: committer date (unix timestamp), %s: subject
            log_format = "%H|%ct|%s"
            cmd = [
                "git", 
                "-C", str(root), 
                "log", 
                f"--pretty=format:{log_format}", 
                f"-n {self.max_commits}", 
                "--no-pager"
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=30,
                check=True
            )

            commits = self._parse_log(result.stdout)
            return GitHistory(
                commits=commits,
                total_commits=len(commits)
            )

        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError) as e:
            logger.error(f"Git history collection failed for {root}: {e}")
            return None
        except Exception as e:
            logger.exception(f"Unexpected error during Git inspection: {e}")
            return None

    def _parse_log(self, output: str) -> list[GitCommit]:
        """
        Parses the git log output into a list of GitCommit objects.
        """
        commits = []
        lines = output.strip().splitlines()
        
        for line in lines:
            if not line:
                continue
            
            parts = line.split("|", 2)
            if len(parts) < 3:
                continue
                
            commit_hash, timestamp_str, message = parts
            
            try:
                timestamp = int(timestamp_str)
                committed_at = datetime.fromtimestamp(timestamp, tz=timezone.utc)
                
                # For each commit, we could potentially fetch changed files.
                # However, doing a 'git show --name-only' for every commit 
                # in a loop can be very slow. We'll fetch changed files 
                # only if specifically requested or for the most recent commits.
                # For the MVP, we'll leave changed_files empty or implement a 
                # limited fetch.
                
                commits.append(GitCommit(
                    hash=commit_hash,
                    message=message,
                    committed_at=committed_at,
                    changed_files=[] 
                ))
            except (ValueError, OSError) as e:
                logger.warning(f"Failed to parse commit line {line}: {e}")
                continue
                
        return commits

    def get_changed_files(self, root: Path, commit_hash: str) -> list[str]:
        """
        Gets the list of files changed in a specific commit.
        """
        try:
            cmd = ["git", "-C", str(root), "show", "--pretty=format:", "--name-only", commit_hash]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=10,
                check=True
            )
            return result.stdout.strip().splitlines()
        except Exception as e:
            logger.error(f"Failed to get changed files for commit {commit_hash}: {e}")
            return []