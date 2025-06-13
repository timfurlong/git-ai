import pytest
from unittest.mock import Mock, patch
from git_ai import generate_pr_description, PRDescription

@pytest.fixture
def mock_pr():
    pr = Mock()
    pr.title = "Add new feature"
    pr.get_files.return_value = [
        Mock(filename="test.py", patch="+def test():\n+    pass"),
        Mock(filename="README.md", patch="+# New Feature\n+Added new functionality")
    ]
    return pr

@pytest.fixture
def mock_repo():
    repo = Mock()
    return repo

@pytest.fixture
def mock_github():
    with patch('git_ai.generate_pr_description.Github') as mock:
        yield mock

@patch.dict('os.environ', {"GH_ACCESS_TOKEN": "dummy"})
@patch('git_ai.generate_pr_description.instructor')
def test_generate_pr_description(mock_instructor, mock_pr, mock_repo, mock_github):
    # Setup
    mock_repo.get_pull.return_value = mock_pr
    mock_github.return_value.get_repo.return_value = mock_repo
    # Patch instructor client to return a dummy PRDescription
    dummy_response = PRDescription(title="Add new feature", files={"test.py": "+def test():\n+    pass", "README.md": "+# New Feature\n+Added new functionality"}, description="This PR adds a new feature.")
    mock_client = Mock()
    mock_client.chat.completions.create.return_value = dummy_response
    mock_instructor.patch.return_value = mock_client
    mock_instructor.from_anthropic.return_value = Mock()
    
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

@patch.dict('os.environ', {"GH_ACCESS_TOKEN": "dummy"})
def test_invalid_pr_url():
    with pytest.raises(ValueError, match="Invalid PR URL"):
        generate_pr_description("invalid-url")

def test_missing_github_token():
    with patch.dict('os.environ', {}, clear=True):
        with pytest.raises(ValueError, match="GH_ACCESS_TOKEN is not set"):
            generate_pr_description("https://github.com/org/repo/pull/123") 