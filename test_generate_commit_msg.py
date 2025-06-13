import os
import pytest
from git import Repo
from generate_commit_msg import smart_diff, generate_commit_msg, get_previous_commit_messages
import tempfile
import shutil
from unittest.mock import patch

@pytest.fixture
def temp_repo():
    """Create a temporary git repository for testing."""
    # Create a temporary directory
    temp_dir = tempfile.mkdtemp()
    
    # Initialize a git repository
    repo = Repo.init(temp_dir)
    
    # Create a test file and commit it
    test_file = os.path.join(temp_dir, "test.txt")
    with open(test_file, "w") as f:
        f.write("initial content")
    
    repo.index.add([test_file])
    repo.index.commit("initial commit")
    
    yield temp_dir
    
    # Cleanup
    shutil.rmtree(temp_dir)

def test_mixed_staged_and_unstaged_changes(temp_repo):
    """Test when there are both staged and unstaged changes."""
    repo = Repo(temp_repo)
    
    # Create two files
    staged_file = os.path.join(temp_repo, "staged.txt")
    unstaged_file = os.path.join(temp_repo, "unstaged.txt")
    
    # Create and stage the first file
    with open(staged_file, "w") as f:
        f.write("staged content")
    repo.index.add([staged_file])
    
    # Create but don't stage the second file
    with open(unstaged_file, "w") as f:
        f.write("unstaged content")
    
    # Get the diff dictionary
    diffs = smart_diff(temp_repo)
    
    # Should only show staged changes
    assert "staged.txt" in diffs
    assert "staged content" in diffs["staged.txt"]
    assert "unstaged.txt" not in diffs

def test_staged_changes(temp_repo):
    """Test when there are staged changes."""
    repo = Repo(temp_repo)
    
    # Modify the test file and stage it
    test_file = os.path.join(temp_repo, "test.txt")
    with open(test_file, "w") as f:
        f.write("modified content")
    repo.index.add([test_file])
    
    # Get the diff dictionary
    diffs = smart_diff(temp_repo)
    
    assert "test.txt" in diffs
    assert "modified content" in diffs["test.txt"]

def test_unstaged_changes(temp_repo):
    """Test when there are unstaged changes."""
    repo = Repo(temp_repo)
    
    # Modify the test file without staging
    test_file = os.path.join(temp_repo, "test.txt")
    with open(test_file, "w") as f:
        f.write("unstaged content")
    
    # Get the diff dictionary
    diffs = smart_diff(temp_repo)
    
    assert "test.txt" in diffs
    assert "unstaged content" in diffs["test.txt"]

def test_untracked_files(temp_repo):
    """Test when there are untracked files."""
    # Create a new untracked file
    new_file = os.path.join(temp_repo, "new.txt")
    with open(new_file, "w") as f:
        f.write("new file content")
    
    # Get the diff dictionary
    diffs = smart_diff(temp_repo)
    
    assert "new.txt" in diffs
    assert "new file content" in diffs["new.txt"]

def test_deleted_files(temp_repo):
    """Test when files are deleted."""
    repo = Repo(temp_repo)
    
    # Delete the test file
    test_file = os.path.join(temp_repo, "test.txt")
    os.remove(test_file)
    
    # Get the diff dictionary
    diffs = smart_diff(temp_repo)
    
    assert "test.txt" in diffs
    assert "deleted" in diffs["test.txt"].lower()

def test_no_changes(temp_repo):
    """Test when there are no changes."""
    # Get the diff dictionary
    diffs = smart_diff(temp_repo)
    
    assert diffs == {}  # Should be empty when no changes

def test_invalid_repo_path():
    """Test with an invalid repository path."""
    with pytest.raises(Exception):
        smart_diff("/nonexistent/path")

def test_generate_commit_msg():
    """Test the commit message generation with mocked API response."""
    # Sample file diffs
    file_diffs = {
        "test.txt": "diff --git a/test.txt b/test.txt\n@@ -1 +1 @@\n-initial content\n+modified content"
    }
    
    # Mock the litellm API response
    mock_response = type('Response', (), {
        'choices': [type('Choice', (), {
            'message': type('Message', (), {
                'content': "Update test.txt with modified content"
            })
        })]
    })
    
    with patch('litellm.completion', return_value=mock_response):
        commit_msg = generate_commit_msg(file_diffs)
        assert commit_msg == "Update test.txt with modified content"

def test_generate_commit_msg_empty_diffs():
    """Test commit message generation with empty diffs."""
    file_diffs = {}
    
    # Mock the litellm API response
    mock_response = type('Response', (), {
        'choices': [type('Choice', (), {
            'message': type('Message', (), {
                'content': "No changes to commit"
            })
        })]
    })
    
    with patch('litellm.completion', return_value=mock_response):
        commit_msg = generate_commit_msg(file_diffs)
        assert commit_msg == "No changes to commit"

def test_generate_commit_msg_multiple_files():
    """Test commit message generation with multiple file changes."""
    file_diffs = {
        "test1.txt": "diff --git a/test1.txt b/test1.txt\n@@ -1 +1 @@\n-old content\n+new content",
        "test2.txt": "diff --git a/test2.txt b/test2.txt\n@@ -1 +1 @@\n-removed\n+added"
    }
    
    # Mock the litellm API response
    mock_response = type('Response', (), {
        'choices': [type('Choice', (), {
            'message': type('Message', (), {
                'content': "Update multiple files: test1.txt and test2.txt"
            })
        })]
    })
    
    with patch('litellm.completion', return_value=mock_response):
        commit_msg = generate_commit_msg(file_diffs)
        assert commit_msg == "Update multiple files: test1.txt and test2.txt"

def test_generate_commit_msg_with_additional_prompt():
    """Test commit message generation with additional prompt context."""
    file_diffs = {
        "test.txt": "diff --git a/test.txt b/test.txt\n@@ -1 +1 @@\n-initial content\n+modified content"
    }
    
    additional_prompt = "This change is part of a larger refactoring effort."
    
    # Mock the litellm API response
    mock_response = type('Response', (), {
        'choices': [type('Choice', (), {
            'message': type('Message', (), {
                'content': "Update test.txt with modified content as part of refactoring"
            })
        })]
    })
    
    with patch('litellm.completion', return_value=mock_response):
        commit_msg = generate_commit_msg(file_diffs, additional_prompt)
        assert commit_msg == "Update test.txt with modified content as part of refactoring"

def test_get_previous_commit_messages(temp_repo):
    """Test retrieving previous commit messages."""
    repo = Repo(temp_repo)
    
    # Create and commit some test files
    for i in range(3):
        test_file = os.path.join(temp_repo, f"test{i}.txt")
        with open(test_file, "w") as f:
            f.write(f"content {i}")
        repo.index.add([test_file])
        repo.index.commit(f"Test commit {i}")
    
    messages = get_previous_commit_messages(temp_repo)
    assert len(messages) == 4  # 3 test commits + 1 initial commit
    assert all(f"Test commit {i}" in messages for i in range(3))
    assert "initial commit" in messages

def test_generate_commit_msg_with_previous_commits():
    """Test commit message generation with previous commit messages included."""
    file_diffs = {
        "test.txt": "diff --git a/test.txt b/test.txt\n@@ -1 +1 @@\n-initial content\n+modified content"
    }
    
    # Mock the previous commit messages
    mock_commits = ["feat: add new feature", "fix: resolve bug", "docs: update README"]
    
    # Mock the litellm API response
    mock_response = type('Response', (), {
        'choices': [type('Choice', (), {
            'message': type('Message', (), {
                'content': "feat: update test.txt with modified content"
            })
        })]
    })
    
    with patch('generate_commit_msg.get_previous_commit_messages', return_value=mock_commits), \
         patch('litellm.completion', return_value=mock_response):
        commit_msg = generate_commit_msg(file_diffs, include_previous_commits=True)
        assert commit_msg == "feat: update test.txt with modified content"

def test_generate_commit_msg_includes_previous_commits_by_default():
    """Test that previous commit messages are included by default."""
    file_diffs = {
        "test.txt": "diff --git a/test.txt b/test.txt\n@@ -1 +1 @@\n-initial content\n+modified content"
    }
    mock_commits = ["feat: add new feature", "fix: resolve bug"]
    mock_response = type('Response', (), {
        'choices': [type('Choice', (), {
            'message': type('Message', (), {
                'content': "feat: update test.txt with modified content"
            })
        })]
    })
    with patch('generate_commit_msg.get_previous_commit_messages', return_value=mock_commits) as prev_patch, \
         patch('litellm.completion', return_value=mock_response) as llm_patch:
        commit_msg = generate_commit_msg(file_diffs)
        # Check that get_previous_commit_messages was called (default behavior)
        prev_patch.assert_called()
        assert commit_msg == "feat: update test.txt with modified content"

def test_generate_commit_msg_excludes_previous_commits_when_disabled():
    """Test that previous commit messages are NOT included when include_previous_commits is False."""
    file_diffs = {
        "test.txt": "diff --git a/test.txt b/test.txt\n@@ -1 +1 @@\n-initial content\n+modified content"
    }
    mock_response = type('Response', (), {
        'choices': [type('Choice', (), {
            'message': type('Message', (), {
                'content': "update test.txt with modified content (no style)"
            })
        })]
    })
    with patch('generate_commit_msg.get_previous_commit_messages') as prev_patch, \
         patch('litellm.completion', return_value=mock_response) as llm_patch:
        commit_msg = generate_commit_msg(file_diffs, include_previous_commits=False)
        # Check that get_previous_commit_messages was NOT called
        prev_patch.assert_not_called()
        assert commit_msg == "update test.txt with modified content (no style)" 