from pathlib import Path
from typing import List, Dict, Any, Optional
from agents import function_tool
from ghost_projects.services.evidence import EvidenceCollector

def create_evidence_tools(root: Path, evidence_collector: EvidenceCollector):
    """
    Creates and returns evidence collection tools.
    """

    @function_tool
    def collect_project_evidence(
        relative_path: str, 
        description: str, 
        excerpt: Optional[str] = None, 
        line_start: Optional[int] = None, 
        line_end: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Records a piece of evidence found during the investigation.
        
        Args:
            relative_path: The path to the file providing the evidence, relative to project root.
            description: A clear description of what this evidence proves or indicates.
            excerpt: The actual text snippet from the file.
            line_start: The starting line number of the excerpt.
            line_end: The ending line number of the excerpt.
        """
        try:
            # Resolve path and ensure it's within root
            clean_path = relative_path.lstrip("/")
            full_path = (root / clean_path).resolve()
            
            if not str(full_path).startswith(str(root.resolve())):
                return {"success": False, "error": "Access denied: Path is outside project root."}
            
            evidence = evidence_collector.create_evidence(
                source_path=str(full_path),
                description=description,
                excerpt=excerpt,
                line_start=line_start,
                line_end=line_end
            )
            
            return {
                "success": True,
                "data": {
                    "evidence_id": evidence.id,
                    "source_path": str(Path(evidence.source_path).relative_to(root)),
                    "description": evidence.description
                }
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    @function_tool
    def get_evidence_details(evidence_id: str) -> Dict[str, Any]:
        """
        Retrieves the full details of a previously collected piece of evidence.
        
        Args:
            evidence_id: The unique identifier of the evidence.
        """
        try:
            evidence = evidence_collector.get_evidence(evidence_id)
            if not evidence:
                return {"success": False, "error": f"Evidence with ID {evidence_id} not found."}
            
            return {
                "success": True,
                "data": {
                    "id": evidence.id,
                    "source_path": str(Path(evidence.source_path).relative_to(root)),
                    "description": evidence.description,
                    "excerpt": evidence.excerpt,
                    "line_start": evidence.line_start,
                    "line_end": evidence.line_end
                }
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    return [collect_project_evidence, get_evidence_details]