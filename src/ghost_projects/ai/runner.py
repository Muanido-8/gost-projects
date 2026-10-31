import logging
from typing import Any

from agents import Runner
from ghost_projects.ai.agent import create_investigation_agent
from ghost_projects.ai.model_provider import get_model_provider
from ghost_projects.config.settings import settings
from ghost_projects.tools.tool_factory import create_project_tools
from ghost_projects.schemas.assessment import ProjectAssessment
from ghost_projects.schemas.project import ProjectInfo
from ghost_projects.ai.parser import parse_assessment
from agents.stream_events import RunItemStreamEvent, RawResponsesStreamEvent
from agents.items import ToolCallItem, ToolCallOutputItem, MessageOutputItem

# Import services for type hinting
from ghost_projects.services.scanner import ProjectScanner
from ghost_projects.services.reader import FileReader
from ghost_projects.services.search import FileSearchService
from ghost_projects.services.git_inspector import GitInspector
from ghost_projects.services.evidence import EvidenceCollector

logger = logging.getLogger(__name__)

async def run_investigation(
    project_info: ProjectInfo,
    scanner: ProjectScanner,
    reader: FileReader,
    search_service: FileSearchService,
    git_inspector: GitInspector,
    evidence_collector: EvidenceCollector,
    max_turns: int = 15
) -> ProjectAssessment:
    """
    Executes the full AI investigation pipeline for a given project.
    
    Args:
        project_info: Information about the project to investigate.
        scanner: Project scanning service.
        reader: File reading service.
        search_service: File search service.
        git_inspector: Git inspection service.
        evidence_collector: Evidence collection service.
        max_turns: Maximum number of agent turns allowed.
        
    Returns:
        A validated ProjectAssessment object.
        
    Raises:
        RuntimeError: If the investigation fails due to provider or execution errors.
        ValueError: If the final output cannot be validated against ProjectAssessment.
    """
    logger.info(f"Starting investigation for project: {project_info.name}")
    
    try:
        # 1. Setup Model and Tools
        model = get_model_provider()
        tools = create_project_tools(
            root=project_info.root_path,
            scanner=scanner,
            reader=reader,
            search_service=search_service,
            git_inspector=git_inspector,
            evidence_collector=evidence_collector
        )
        
        # 2. Create Agent
        agent = create_investigation_agent(model, tools)
        
        # 3. Execute Investigation
        # We start the conversation by telling the agent which project it is investigating
        initial_message = (
            f"Please investigate the following project:\n"
            f"Name: {project_info.name}\n"
            f"Root Path: {project_info.root_path}\n"
            f"Detected Languages: {', '.join(project_info.detected_languages)}\n"
            f"Detected Technologies: {', '.join(project_info.detected_technologies)}\n"
            f"Has Git: {project_info.has_git}\n\n"
            "Please follow the investigation workflow and produce a final ProjectAssessment to decide if the project can come to live again or not."
        )
        
        result = await Runner.run(
            agent,
            input=initial_message,
            max_turns=max_turns
        )
        # result = Runner.run_streamed(
        #     agent,
        #     input=initial_message,
        #     max_turns=max_turns
        # )
        # turn = 0
        # async for event in result.stream_events():
        #     print("# Evento acontecento")

        assessment = parse_assessment(
            result.final_output,
            ProjectAssessment,
        )

        return assessment

    except Exception as e:
        logger.exception(f"Investigation failed for {project_info.name}: {e}")
        if isinstance(e, (ValueError, RuntimeError)):
            raise e
        raise RuntimeError(f"An unexpected error occurred during investigation: {e}") from e