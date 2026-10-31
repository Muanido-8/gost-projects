from pathlib import Path
from typing import List, Dict, Any, Optional
from agents import function_tool
from ghost_projects.services.search import FileSearchService, SearchOptions
from ghost_projects.services.scanner import ProjectScanner

def create_search_tools(root: Path, search_service: FileSearchService, scanner: ProjectScanner):
    """
    Creates and returns file discovery and search tools.
    """

    @function_tool
    def search_project_files(extension: Optional[str] = None, max_results: int = 100) -> List[Dict[str, Any]]:
        """
        Finds project files based on extension.
        
        Args:
            extension: The file extension to filter by (e.g., '.py', '.js').
            max_results: Maximum number of files to return.
        """
        try:
            files = []
            for f in scanner.scan(root):
                if extension and f.extension != extension:
                    continue
                
                files.append({
                    "path": str(f.path.relative_to(root)),
                    "name": f.name,
                    "size_bytes": f.size_bytes
                })
                
                if len(files) >= max_results:
                    break
            
            return files
        except Exception as e:
            return [{"error": str(e)}]

    @function_tool
    def find_in_files(query: str, use_regex: bool = False, case_sensitive: bool = False, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Searches for a term or pattern within the contents of project files.
        
        Args:
            query: The text or regex pattern to search for.
            use_regex: Whether to treat the query as a regular expression.
            case_sensitive: Whether the search should be case sensitive.
            max_results: Maximum number of matches to return.
        """
        try:
            options = SearchOptions(
                query=query,
                use_regex=use_regex,
                case_sensitive=case_sensitive,
                max_results=max_results
            )
            
            matches = []
            for match in search_service.search(root, options):
                matches.append({
                    "path": str(match.path.relative_to(root)),
                    "line": match.line_number,
                    "text": match.matched_text,
                    "context": match.context
                })
                
                if len(matches) >= max_results:
                    break
            
            return matches
        except Exception as e:
            return [{"error": str(e)}]

    return [search_project_files, find_in_files]