import argparse
import json
import os
import re
from typing import Dict, List

import litellm
from dotenv import load_dotenv
from github import Auth, Github
from pydantic import BaseModel

# Use the .env file located in the same directory as this script
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"), override=True)

# Get the model from environment variable, defaulting to gpt-4o
model = os.getenv("LITELLM_MODEL", "openai/gpt-4o")

class PRDescription(BaseModel):
    title: str
    files: Dict[str, str]
    description: str

def generate_pr_description(pr_url: str, additional_text: str = None) -> PRDescription:
    # Parse out org, repo, and PR number using the pattern: github.com/{org}/{repo}/pull/{pr_number}
    match = re.search(r"github.com/([^/]+)/([^/]+)/pull/(\d+)/{0,1}", pr_url)
    if not match:
        raise ValueError(f"Invalid PR URL: {pr_url!r}")
    org, repo, pr_number = match.groups()
    pr_number = int(pr_number)

    # Check that the GH_ACCESS_TOKEN is set
    if "GH_ACCESS_TOKEN" not in os.environ:
        raise ValueError("GH_ACCESS_TOKEN is not set")
    # Create a Github instance
    auth = Auth.Token(os.environ["GH_ACCESS_TOKEN"])
    g = Github(auth=auth)

    # Get the PR
    repo = g.get_repo(f"{org}/{repo}")
    pr = repo.get_pull(pr_number)

    # Get the PR title
    pr_title = pr.title

    # Get a mapping of PR files to their patch
    pr_contents = {pr_file.filename: pr_file.patch for pr_file in pr.get_files()}

    # Create the prompt
    prompt = f"""
    Given the following information for a GitHub Pull Request, write a description for the
    PR. The description should be clear, concise, and highlight the key changes made.

    Pull Request title: "{pr_title}"

    Pull Request contents (provided as a mapping of filename to change information):
    ```json
    {json.dumps(pr_contents, indent=2)}
    ```

    Please provide your response in the following JSON format:
    {{
        "title": "The PR title",
        "files": {{
            "filename1": "file contents",
            "filename2": "file contents"
        }},
        "description": "Your detailed PR description"
    }}
    """

    if additional_text:
        prompt += additional_text

    # Generate the description using LiteLLM
    response = litellm.completion(
        model=model,
        messages=[{"role": "user", "content": prompt}]
    )
    
    try:
        # Parse the response into a PRDescription object
        response_content = json.loads(response.choices[0].message.content)
        return PRDescription(**response_content)
    except json.JSONDecodeError as e:
        # If JSON parsing fails, try to extract the description from the text
        content = response.choices[0].message.content
        return PRDescription(
            title=pr_title,
            files=pr_contents,
            description=content
        )

def get_args():
    parser = argparse.ArgumentParser(
        description="Pull the GitHub pull request contents to generate a description "
        "using an LLM"
    )
    # Pull request URL
    parser.add_argument(
        "pr_url", help="The URL of the pull request to generate the description for"
    )
    # Optional argument to add additional text to the prompt
    parser.add_argument(
        "-a",
        "--additional_text",
        help="Additional text to add to the user message prompt",
    )
    return parser.parse_args()

if __name__ == "__main__":
    args = get_args()
    result = generate_pr_description(args.pr_url, args.additional_text)
    print(result.description)
