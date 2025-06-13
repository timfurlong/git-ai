"""
Generate a commit message for the current changes.
"""

import os
from git import Repo, InvalidGitRepositoryError, NoSuchPathError
import litellm
import sys
import subprocess
import re
import argparse

model = os.getenv("LITELLM_MODEL", "openai/gpt-4o")

from git import Repo
import sys, os

def get_file_diffs(diff_text, max_lines=100):
    """
    Returns a dict: {filename: diff_output (possibly truncated)}
    """
    file_diffs = re.split(r'(?=^diff --git )', diff_text, flags=re.MULTILINE)
    result = {}
    for file_diff in file_diffs:
        if not file_diff.strip():
            continue
        # Extract filename from the diff header
        match = re.search(r'^diff --git a/(.*?) b/(.*?)$', file_diff, re.MULTILINE)
        if match:
            filename = match.group(2)
        else:
            filename = 'unknown'
        lines = file_diff.splitlines()
        if len(lines) > max_lines:
            truncated = "\n".join(lines[:max_lines]) + f"\n[...truncated {len(lines) - max_lines} lines for this file...]"
            result[filename] = truncated
        else:
            result[filename] = file_diff
    return result

def smart_diff(repo_path=".", max_lines=100):
    repo = Repo(repo_path)

    # Any staged changes?
    if repo.index.diff("HEAD"):
        output = repo.git.diff("--cached")
    else:
        # Nothing staged → show working-tree edits first
        output = repo.git.diff()   # modified / deleted files

        # Append a patch for each untracked file
        for path in repo.untracked_files:
            # Skip files that are git-ignored (just in case untracked_files was filtered)
            if os.path.isdir(os.path.join(repo.working_tree_dir, path)):
                continue  # ignore untracked directories; remove if you want them

            try:
                # Use subprocess directly to handle the non-zero exit code
                result = subprocess.run(
                    ["git", "diff", "--no-index", "/dev/null", path],
                    capture_output=True,
                    text=True,
                    cwd=repo.working_tree_dir
                )
                if result.stdout:
                    output += result.stdout
            except subprocess.CalledProcessError:
                # Ignore the error as it's expected for new files
                pass

    if output:
        return get_file_diffs(output, max_lines=max_lines)
    else:
        return {}

def get_previous_commit_messages(repo_path=".", num_commits=10):
    """
    Get the previous commit messages from the repository.
    
    Args:
        repo_path (str): Path to the git repository
        num_commits (int): Number of previous commits to retrieve
        
    Returns:
        list: List of previous commit messages
    """
    repo = Repo(repo_path)
    commits = list(repo.iter_commits(max_count=num_commits))
    return [commit.message.strip() for commit in commits]

def generate_commit_msg(file_diffs, additional_prompt=None, include_previous_commits=True, feedback=None):
    """
    Generate a commit message for the current changes.
    
    Args:
        file_diffs (dict): Dictionary of file diffs
        additional_prompt (str, optional): Additional sentences to add to the prompt
        include_previous_commits (bool): Whether to include previous commit messages in the prompt
        feedback (str, optional): User feedback to incorporate into the commit message
    """
    # Format the file diffs in a way that is easier for the model to understand
    formatted_diffs = ""
    for filename, diff in file_diffs.items():
        formatted_diffs += f"File: {filename}\n"
        formatted_diffs += f"```\n{diff}\n```\n"

    prompt = f"""
    You are a helpful assistant that generates a commit message for the current changes.
    Only provide the commit message, no other text.

    The changes are described in the following diffs:
    {formatted_diffs}
    """
    
    if include_previous_commits:
        previous_commits = get_previous_commit_messages()
        if previous_commits:
            prompt += "\nHere are some previous commit messages to follow the same style:\n"
            for i, msg in enumerate(previous_commits, 1):
                prompt += f"{i}. {msg}\n"
    
    if additional_prompt:
        prompt += f"\nAdditional context: {additional_prompt}"
        
    if feedback:
        prompt += f"\n\nUser feedback on the previous commit message: {feedback}\nPlease revise the commit message based on this feedback."
        
    response = litellm.completion(model=model, messages=[{"role": "user", "content": prompt}])
    return response.choices[0].message.content

def interactive_commit_msg(file_diffs, additional_prompt=None, include_previous_commits=True):
    """
    Interactively generate a commit message with user feedback.
    
    Args:
        file_diffs (dict): Dictionary of file diffs
        additional_prompt (str, optional): Additional sentences to add to the prompt
        include_previous_commits (bool): Whether to include previous commit messages in the prompt
    
    Returns:
        str: The final accepted commit message
    """
    feedback = None
    while True:
        commit_msg = generate_commit_msg(
            file_diffs,
            additional_prompt=additional_prompt,
            include_previous_commits=include_previous_commits,
            feedback=feedback
        )
        print("\nGenerated commit message:")
        print(commit_msg)
        user_feedback = input("\nPress Enter to accept, or type feedback to revise: ").strip()
        if not user_feedback:
            return commit_msg
        feedback = user_feedback

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a commit message for the current changes.")
    parser.add_argument("--prompt", "-p", type=str, help="Additional sentences to add to the prompt")
    parser.add_argument("--no-previous", action="store_true", 
                      help="Do NOT include previous commit messages in the prompt (default: include them)")
    args = parser.parse_args()
    
    file_diffs = smart_diff()
    print(interactive_commit_msg(file_diffs, args.prompt, not args.no_previous))