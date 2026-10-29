import hashlib
import logging
from pathlib import Path
from typing import Optional

from ghost_projects.types.evidence import Evidence

logger = logging.getLogger(__name__)

class EvidenceCollector:
    """
    Responsible for collecting and organizing evidence that can support the AI investigation.
    """

    def __init__(self):
        # Store evidence by ID to avoid duplicates
        self._evidence_store: dict[str, Evidence] = {}

    def create_evidence(
        self, 
        source_path: Path, 
        description: str, 
        excerpt: Optional[str] = None, 
        line_start: Optional[int] = None, 
        line_end: Optional[int] = None
    ) -> Evidence:
        """
        Creates a stable evidence identifier and stores the evidence.
        
        Args:
            source_path: Path to the file providing the evidence.
            description: Description of what this evidence proves.
            excerpt: The actual text snippet from the file.
            line_start: Starting line number.
            line_end: Ending line number.
            
        Returns:
            The created Evidence object.
        """
        # Generate a stable ID based on path and a hash of the description/excerpt
        # This ensures that the same observation from the same file gets the same ID
        id_seed = f"{source_path}:{description}:{excerpt or ''}:{line_start or 0}"
        evidence_id = f"ev_{hashlib.sha256(id_seed.encode()).hexdigest()[:12]}"

        if evidence_id in self._evidence_store:
            return self._evidence_store[evidence_id]

        evidence = Evidence(
            id=evidence_id,
            source_path=source_path,
            description=description,
            excerpt=excerpt,
            line_start=line_start,
            line_end=line_end
        )

        self._evidence_store[evidence_id] = evidence
        return evidence

    def get_evidence(self, evidence_id: str) -> Optional[Evidence]:
        """
        Retrieves evidence by its identifier.
        """
        return self._evidence_store.get(evidence_id)

    def get_all_evidence(self) -> list[Evidence]:
        """
        Returns all collected evidence.
        """
        return list(self._evidence_store.values())

    def clear(self):
        """
        Clears the collected evidence store.
        """
        self._evidence_store.clear()