from pathlib import Path
from typing import List, Dict, Any
from agents import function_tool
from ghost_projects.services.scanner import ProjectScanner

def create_project_tools(root: Path, scanner: ProjectScanner):
    """
    Creates and returns project inspection tools.
    """

    @function_tool
    def inspect_project() -> Dict[str, Any]:
        """
        Obtains a high-level overview of the target project.
        
        Returns a summary including detected files, total count, and basic project metadata.
        """
        try:
            files = list(scanner.scan(root))
            total_files = len(files)
            extensions = {}
            for f in files:
                if not f.is_directory:
                    extensions[f.extension] = extensions.get(f.extension, 0) + 1
            
            return {
                "success": True,
                "data": {
                    "project_root": str(root),
                    "total_files": total_files,
                    "extensions": extensions,
                    "is_git_repo": (root / ".git").exists(),
                }
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    @function_tool
    def get_project_structure(max_depth: int = 3, max_files: int = 100) -> str:
        """
        Returns a bounded, readable representation of the project tree.
        
        Args:
            max_depth: Maximum depth to traverse.
            max_files: Maximum number of files to include in the output.
            
        Returns:
            A string representation of the project structure.
        """
        try:
            files = list(scanner.scan(root))
            
            # Simple tree construction
            lines = [f"Project Root: {root.name}/"]
            count = 0
            
            # Sort files by path to group them
            sorted_files = sorted(files, key=lambda x: str(x.path))
            
            for f in sorted_files:
                if count >= max_files:
                    lines.append("... (max files reached)")
                    break
                
                # Calculate depth relative to root
                relative_path = f.path.relative_to(root)
                depth = len(relative_path.parts)
                
                if depth > max_depth:
                    continue
                
                indent = "  " * (depth - 1)
                prefix = "└── " if depth > 0 else ""
                suffix = "/" if f.is_directory else ""
                
                lines.append(f"{indent}{prefix}{f.name}{suffix}")
                count += 1
                
            return "\n".join(lines)
        except Exception as e:
            return f"Error retrieving project structure: {str(e)}"

    return [inspect_project, get_project_structure]