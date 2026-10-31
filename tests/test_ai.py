import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from pathlib import Path

from agents.models.interface import Model
from ghost_projects.ai.model_provider import get_model_provider
from ghost_projects.ai.agent import create_investigation_agent
from ghost_projects.ai.runner import run_investigation
from ghost_projects.schemas.project import ProjectInfo
from ghost_projects.schemas.assessment import ProjectAssessment
from ghost_projects.schemas.finding import Finding, FindingCategory
from ghost_projects.schemas.evidence import Evidence

@pytest.fixture
def mock_project_info():
    return ProjectInfo(
        name="Test Project",
        root_path=Path("/tmp/test_project"),
        detected_languages=["python"],
        detected_technologies=["pydantic"],
        has_git=True
    )

@pytest.fixture
def mock_services():
    return {
        "scanner": MagicMock(),
        "reader": MagicMock(),
        "search_service": MagicMock(),
        "git_inspector": MagicMock(),
        "evidence_collector": MagicMock(),
    }

@patch("ghost_projects.ai.model_provider.AsyncOpenAI")
def test_model_provider_config(mock_async_openai):
    """Test that the model provider is configured with settings."""
    get_model_provider()
    mock_async_openai.assert_called_once()
    args, kwargs = mock_async_openai.call_args
    assert "base_url" in kwargs
    assert "api_key" in kwargs

def test_agent_creation(mock_services):
    """Test that the agent is created with correct properties."""
    # Create a mock that satisfies isinstance(model, Model)
    mock_model = MagicMock(spec=Model)
    mock_tools = [MagicMock()]
    
    agent = create_investigation_agent(mock_model, mock_tools)
    
    assert agent.name == "Ghost Projects Archaeologist"
    assert agent.model == mock_model
    assert agent.tools == mock_tools
    assert agent.output_type == ProjectAssessment

@pytest.mark.anyio
@patch("ghost_projects.ai.runner.Runner.run")
@patch("ghost_projects.ai.runner.get_model_provider")
async def test_run_investigation_success(
    mock_get_provider, 
    mock_runner_run, 
    mock_project_info, 
    mock_services
):
    """Test successful investigation flow."""
    # Setup mock result
    expected_assessment = ProjectAssessment(
        purpose="Test Purpose",
        summary="A test project",
        architecture="Test Architecture",
        findings=[],
        evidence=[],
        recovery_plan=[],
        unknowns=[]
    )
    mock_runner_run.return_value = expected_assessment
    mock_get_provider.return_value = MagicMock(spec=Model)

    result = await run_investigation(
        project_info=mock_project_info,
        **mock_services
    )

    assert isinstance(result, ProjectAssessment)
    assert result.summary == "A test project"
    mock_runner_run.assert_called_once()

@pytest.mark.anyio
@patch("ghost_projects.ai.runner.Runner.run")
@patch("ghost_projects.ai.runner.get_model_provider")
async def test_run_investigation_validation_failure(
    mock_get_provider, 
    mock_runner_run, 
    mock_project_info, 
    mock_services
):
    """Test that invalid model output raises ValueError."""
    # Return a dict that is missing required fields for ProjectAssessment
    mock_runner_run.return_value = {"invalid": "data"}
    mock_get_provider.return_value = MagicMock(spec=Model)

    with pytest.raises(ValueError, match="AI produced invalid assessment structure"):
        await run_investigation(
            project_info=mock_project_info,
            **mock_services
        )

@pytest.mark.anyio
@patch("ghost_projects.ai.runner.Runner.run")
@patch("ghost_projects.ai.runner.get_model_provider")
async def test_run_investigation_provider_error(
    mock_get_provider, 
    mock_runner_run, 
    mock_project_info, 
    mock_services
):
    """Test that provider errors are wrapped in RuntimeError."""
    mock_runner_run.side_effect = Exception("API Connection Error")
    mock_get_provider.return_value = MagicMock(spec=Model)

    with pytest.raises(RuntimeError, match="An unexpected error occurred during investigation"):
        await run_investigation(
            project_info=mock_project_info,
            **mock_services
        )

def test_evidence_reference_validation():
    """
    Verify that the existing ProjectAssessment validation 
    rejects findings with non-existent evidence.
    This ensures the AI module cannot bypass existing rules.
    """
    finding = Finding(
        title="Bug",
        description="Found a bug",
        category=FindingCategory.BUG_OR_RISK,
        confidence=0.8,
        evidence_ids=["ev_nonexistent"]
    )
    
    # ProjectAssessment should raise error if evidence_ids are not provided in evidence list
    with pytest.raises(ValueError):
        ProjectAssessment(
            project_name="Test",
            summary="Summary",
            findings=[finding],
            recovery_actions=[],
            evidence=[] # Empty evidence list, but finding references one
        )