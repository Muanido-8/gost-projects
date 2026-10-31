from pathlib import Path
from typing import List, Any
from ghost_projects.services.scanner import ProjectScanner
from ghost_projects.services.reader import FileReader
from ghost_projects.services.search import FileSearchService
from ghost_projects.services.git_inspector import GitInspector
from ghost_projects.services.evidence import EvidenceCollector

from ghost_projects.tools.project_tools import create_project_tools as create_proj
from ghost_projects.tools.file_tools import create_file_tools as create_file
from ghost_projects.tools.search_tools import create_search_tools as create_search
from ghost_projects.tools.git_tools import create_git_tools as create_git
from ghost_projects.tools.evidence_tools import create_evidence_tools as create_evid

def create_project_tools(
    root: Path,
    scanner: ProjectScanner,
    reader: FileReader,
    search_service: FileSearchService,
    git_inspector: GitInspector,
    evidence_collector: EvidenceCollector
) -> List[Any]:
    """
    Factory that creates and returns the complete list of registered tools
    for the Ghost Projects AI agent.
    
    Args:
        root: The root directory of the project being inspected.
        scanner: The project scanning service.
        reader: The file reading service.
        search_service: The file search service.
        git_inspector: The Git inspection service.
        evidence_collector: The evidence collection service.
        
    Returns:
        A list of SDK-compatible function-tool objects.
    """
    all_tools = []
    
    # Project inspection tools
    all_tools.extend(create_proj(root, scanner))
    
    # File inspection tools
    all_tools.extend(create_file(root, reader, scanner))
    
    # Search and discovery tools
    all_tools.extend(create_search(root, search_service, scanner))
    
    # Git tools
    all_tools.extend(create_git(root, git_inspector))
    
    # Evidence tools
    all_tools.extend(create_evid(root, evidence_collector))
    
    return all_tools