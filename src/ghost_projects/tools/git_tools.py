from pathlib import Path
from typing import List, Dict, Any, Optional
from agents import function_tool
from ghost_projects.services.git_inspector import GitInspector

def create_git_tools(root: Path, git_inspector: GitInspector):
    """
    Creates and returns Git inspection tools.
    """

    @function_tool
    def inspect_git_history(max_commits: int = 20) -> Dict[str, Any]:
        """
        Retrieves recent Git commit history for the project.
        
        Args:
            max_commits: Maximum number of recent commits to retrieve.
        """
        try:
            if not git_inspector.is_git_repository(root):
                return {"success": False, "error": "Project is not a Git repository"}
            
            # Note: GitInspector.get_history uses its own internal max_commits from __init__
            # We can't easily change it per call unless we modify the service, 
            # but we can slice the result.
            history = git_inspector.get_history(root)
            
            if not history:
                return {"success": False, "error": "Could not retrieve Git history"}
            
            commits = []
            for c in history.commits[:max_commits]:
                commits.append({
                    "hash": c.hash,
                    "message": c.message,
                    "date": c.committed_at.isoformat(),
                    "changed_files_count": len(c.changed_files)
                })
            
            return {
                "success": True,
                "data": {
                    "total_commits": history.total_commits,
                    "recent_commits": commits
                }
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    @function_tool
    def inspect_file_history(commit_hash: str) -> Dict[str, Any]:
        """
        Retrieves the list of files changed in a specific Git commit.
        
        Args:
            commit_hash: The hash of the commit to inspect.
        """
        try:
            if not git_inspector.is_git_repository(root):
                return {"success": False, "error": "Project is not a Git repository"}
            
            files = git_inspector.get_changed_files(root, commit_hash)
            
            return {
                "success": True,
                "data": {
                    "commit_hash": commit_hash,
                    "changed_files": files
                }
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    return [inspect_git_history, inspect_file_history]