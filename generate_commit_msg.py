"""
Generate a commit message for the current changes.
"""

import os
from git import Repo, InvalidGitRepositoryError, NoSuchPathError
import litellm
import sys
import subprocess
import re

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

def generate_commit_msg(file_diffs):
    """
    Generate a commit message for the current changes.
    """
    # Format the file diffs in a way that is easier for the model to understand
    formatted_diffs = ""
    for filename, diff in file_diffs.items():
        formatted_diffs += f"File: {filename}\n"
        formatted_diffs += f"```\n{diff}\n```\n"

    prompt = f"""
    You are a helpful assistant that generates a commit message for the current changes.
    The changes are described in the following diffs:
    {formatted_diffs}
    """
    response = litellm.completion(model=model, messages=[{"role": "user", "content": prompt}])
    return response.choices[0].message.content

if __name__ == "__main__":
    import pprint
    file_diffs = smart_diff()
    # pprint.pprint(file_diffs)
    print(generate_commit_msg(file_diffs))