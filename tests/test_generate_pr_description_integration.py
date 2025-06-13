import os
import pytest
from git_ai import generate_pr_description, PRDescription

# Skip all tests in this file by default unless INTEGRATION_TESTS is set
pytestmark = pytest.mark.skipif(
    not os.getenv("INTEGRATION_TESTS"),
    reason="Integration tests are disabled. Set INTEGRATION_TESTS=1 to run them."
)

@pytest.fixture
def mock_pr(mocker):
    pr = mocker.Mock()
    pr.title = "Add new feature"
    pr.get_files.return_value = [
        mocker.Mock(filename="test.py", patch="+def test():\n+    pass"),
        mocker.Mock(filename="README.md", patch="+# New Feature\n+Added new functionality")
    ]
    return pr

@pytest.fixture
def mock_repo(mocker):
    repo = mocker.Mock()
    return repo

@pytest.fixture
def mock_github(mocker):
    yield mocker.patch('git_ai.generate_pr_description.Github')

@pytest.mark.integration
def test_generate_pr_description_gpt4(mocker, mock_pr, mock_repo, mock_github):
    mocker.patch.dict('os.environ', {
        "GH_ACCESS_TOKEN": "dummy",
        "LITELLM_MODEL": "openai/gpt-4o"
    })
    # Setup
    mock_repo.get_pull.return_value = mock_pr
    mock_github.return_value.get_repo.return_value = mock_repo
    
    # Test data
    pr_url = "https://github.com/org/repo/pull/123"
    
    # Execute
    result = generate_pr_description(pr_url)
    
    # Assert
    assert isinstance(result, PRDescription)
    assert result.title == "Add new feature"
    assert len(result.files) == 2
    assert "test.py" in result.files
    assert "README.md" in result.files
    assert result.description  # Should have a non-empty description

@pytest.mark.integration
def test_generate_pr_description_bedrock(mocker, mock_pr, mock_repo, mock_github):
    mocker.patch.dict('os.environ', {
        "GH_ACCESS_TOKEN": "dummy",
        "LITELLM_MODEL": "anthropic/claude-3-sonnet-20240229-v1:0"
    })
    # Setup
    mock_repo.get_pull.return_value = mock_pr
    mock_github.return_value.get_repo.return_value = mock_repo
    
    # Test data
    pr_url = "https://github.com/org/repo/pull/123"
    
    # Execute
    result = generate_pr_description(pr_url)
    
    # Assert
    assert isinstance(result, PRDescription)
    assert result.title == "Add new feature"
    assert len(result.files) == 2
    assert "test.py" in result.files
    assert "README.md" in result.files
    assert result.description  # Should have a non-empty description 