from pathlib import Path
from typing import List, Dict, Any, Union
from agents import function_tool
from ghost_projects.services.reader import FileReader
from ghost_projects.services.scanner import ProjectScanner

def create_file_tools(root: Path, reader: FileReader, scanner: ProjectScanner):
    """
    Creates and returns file inspection tools.
    """

    def _safe_path(relative_path: str) -> Path:
        """
        Resolves a relative path and ensures it is within the project root.
        """
        # Remove leading slashes to prevent absolute path interpretation
        clean_path = relative_path.lstrip("/")
        full_path = (root / clean_path).resolve()
        
        if not str(full_path).startswith(str(root.resolve())):
            raise PermissionError(f"Access denied: Path {relative_path} is outside project root.")
        
        return full_path

    @function_tool
    def get_file_info(relative_path: str) -> Dict[str, Any]:
        """
        Returns metadata for a file, such as its extension and size.
        
        Args:
            relative_path: The path to the file relative to the project root.
        """
        try:
            path = _safe_path(relative_path)
            if not path.exists():
                return {"success": False, "error": "File not found"}
            
            stats = path.stat()
            return {
                "success": True,
                "data": {
                    "path": relative_path,
                    "name": path.name,
                    "extension": path.suffix,
                    "size_bytes": stats.st_size,
                    "is_directory": path.is_dir()
                }
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    @function_tool
    def read_file(relative_path: str) -> Dict[str, Any]:
        """
        Reads the content of a single text or configuration file.
        
        Args:
            relative_path: The path to the file relative to the project root.
        """
        try:
            path = _safe_path(relative_path)
            result = reader.read_file(path)
            
            # result is either FileContent or FileReadError
            if hasattr(result, "content"):
                return {
                    "success": True,
                    "data": {
                        "content": result.content,
                        "truncated": result.truncated,
                        "path": str(result.path.relative_to(root))
                    }
                }
            else:
                return {
                    "success": False,
                    "error": result.reason
                }
        except Exception as e:
            return {"success": False, "error": str(e)}

    @function_tool
    def read_multiple_files(relative_paths: List[str]) -> List[Dict[str, Any]]:
        """
        Reads multiple files in one call.
        
        Args:
            relative_paths: A list of paths relative to the project root.
        """
        results = []
        for rel_path in relative_paths:
            try:
                path = _safe_path(rel_path)
                result = reader.read_file(path)
                
                if hasattr(result, "content"):
                    results.append({
                        "path": rel_path,
                        "success": True,
                        "content": result.content,
                        "truncated": result.truncated
                    })
                else:
                    results.append({
                        "path": rel_path,
                        "success": False,
                        "error": result.reason
                    })
            except Exception as e:
                results.append({
                    "path": rel_path,
                    "success": False,
                    "error": str(e)
                })
        return results

    return [get_file_info, read_file, read_multiple_files]