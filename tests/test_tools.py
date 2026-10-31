import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch
from ghost_projects.tools.tool_factory import create_project_tools
from ghost_projects.services.scanner import ProjectScanner
from ghost_projects.services.reader import FileReader
from ghost_projects.services.search import FileSearchService
from ghost_projects.services.git_inspector import GitInspector
from ghost_projects.services.evidence import EvidenceCollector
from ghost_projects.schemas.file import ProjectFile, FileContent

@pytest.fixture
def mock_services():
    return {
        "scanner": MagicMock(spec=ProjectScanner),
        "reader": MagicMock(spec=FileReader),
        "search_service": MagicMock(spec=FileSearchService),
        "git_inspector": MagicMock(spec=GitInspector),
        "evidence_collector": MagicMock(spec=EvidenceCollector),
        "root": Path("C:/fake/project")
    }

def test_tool_factory_returns_all_tools(mock_services):
    tools = create_project_tools(
        mock_services["root"],
        mock_services["scanner"],
        mock_services["reader"],
        mock_services["search_service"],
        mock_services["git_inspector"],
        mock_services["evidence_collector"]
    )
    
    # 2 project + 3 file + 2 search + 2 git + 2 evidence = 11 tools
    assert len(tools) == 11
    for tool in tools:
        # Check if it's a function_tool (should have a name and description)
        assert hasattr(tool, "name")
        assert hasattr(tool, "description")

def test_read_file_success(mock_services):
    tools = create_project_tools(
        mock_services["root"],
        mock_services["scanner"],
        mock_services["reader"],
        mock_services["search_service"],
        mock_services["git_inspector"],
        mock_services["evidence_collector"]
    )
    
    read_file_tool = next(t for t in tools if t.name == "read_file")
    
    # Mock the reader to return a FileContent object
    mock_content = FileContent(path=mock_services["root"] / "test.txt", content="hello world", truncated=False)
    mock_services["reader"].read_file.return_value = mock_content
    
    result = read_file_tool.__wrapped__("test.txt")
    
    assert result["success"] is True
    assert result["data"]["content"] == "hello world"
    mock_services["reader"].read_file.assert_called_once()

def test_path_traversal_prevention(mock_services):
    tools = create_project_tools(
        mock_services["root"],
        mock_services["scanner"],
        mock_services["reader"],
        mock_services["search_service"],
        mock_services["git_inspector"],
        mock_services["evidence_collector"]
    )
    
    read_file_tool = next(t for t in tools if t.name == "read_file")
    
    # Attempt to access outside root
    result = read_file_tool.__wrapped__("../secret.txt")
    
    assert result["success"] is False
    assert "Access denied" in result["error"]

def test_inspect_project_serialization(mock_services):
    tools = create_project_tools(
        mock_services["root"],
        mock_services["scanner"],
        mock_services["reader"],
        mock_services["search_service"],
        mock_services["git_inspector"],
        mock_services["evidence_collector"]
    )
    
    inspect_tool = next(t for t in tools if t.name == "inspect_project")
    
    # Mock scanner to return a few files
    mock_services["scanner"].scan.return_value = [
        ProjectFile(path=mock_services["root"] / "main.py", name="main.py", extension=".py", size_bytes=100, is_directory=False),
        ProjectFile(path=mock_services["root"] / "README.md", name="README.md", extension=".md", size_bytes=200, is_directory=False),
    ]
    
    result = inspect_tool.__wrapped__()
    
    assert result["success"] is True
    assert result["data"]["total_files"] == 2
    assert result["data"]["extensions"] == {".py": 1, ".md": 1}

def test_git_history_no_repo(mock_services):
    tools = create_project_tools(
        mock_services["root"],
        mock_services["scanner"],
        mock_services["reader"],
        mock_services["search_service"],
        mock_services["git_inspector"],
        mock_services["evidence_collector"]
    )
    
    git_tool = next(t for t in tools if t.name == "inspect_git_history")
    mock_services["git_inspector"].is_git_repository.return_value = False
    
    result = git_tool.__wrapped__()
    
    assert result["success"] is False
    assert "not a Git repository" in result["error"]