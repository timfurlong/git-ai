import pytest
from git_ai import generate_pr_description, PRDescription
import json

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


def test_generate_pr_description(mocker, mock_pr, mock_repo, mock_github):
    mocker.patch.dict('os.environ', {"GH_ACCESS_TOKEN": "dummy"})
    mock_repo.get_pull.return_value = mock_pr
    mock_github.return_value.get_repo.return_value = mock_repo
    
    # Mock LiteLLM response
    mock_litellm = mocker.patch('git_ai.generate_pr_description.litellm')
    mock_response = mocker.Mock()
    mock_response.choices = [mocker.Mock(message=mocker.Mock(content=json.dumps({
        "title": "Add new feature",
        "files": {
            "test.py": "+def test():\n+    pass",
            "README.md": "+# New Feature\n+Added new functionality"
        },
        "description": "This PR adds a new feature."
    })))]
    mock_litellm.completion.return_value = mock_response
    
    # Test data
    pr_url = "https://github.com/org/repo/pull/123"
    
    # Execute
    result = generate_pr_description(pr_url)
    print(result)
    
    # Assert
    assert isinstance(result, PRDescription)
    assert result.title == "Add new feature"
    assert len(result.files) == 2
    assert "test.py" in result.files
    assert "README.md" in result.files

def test_invalid_pr_url(mocker):
    mocker.patch.dict('os.environ', {"GH_ACCESS_TOKEN": "dummy"})
    with pytest.raises(ValueError, match="Invalid PR URL"):
        generate_pr_description("invalid-url")

def test_missing_github_token(mocker):
    mocker.patch.dict('os.environ', {}, clear=True)
    with pytest.raises(ValueError, match="GH_ACCESS_TOKEN is not set"):
        generate_pr_description("https://github.com/org/repo/pull/123") 