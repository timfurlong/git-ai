# Git AI

An AI-powered Git assistant that helps automate two key aspects of the development workflow:
1. Generating meaningful commit messages
2. Creating detailed pull request descriptions

## Features

- **Commit Message Generation**: Automatically generates descriptive and conventional commit messages based on your code changes
- **PR Description Generation**: Creates comprehensive pull request descriptions using AI
- Integrates with GitHub's API
- Uses AWS Bedrock for AI capabilities
- Configurable and extensible

## Prerequisites

- Python 3.8 or higher
- GitHub account and access token
- AWS account with Bedrock access (for AI capabilities)
- uv package manager

## Installation

1. Install uv if you haven't already:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. Clone the repository:
```bash
git clone https://github.com/yourusername/git-ai.git
cd git-ai
```

3. Create a virtual environment and install dependencies:
```bash
uv venv
source .venv/bin/activate  # On Unix/macOS
# or
.venv\Scripts\activate  # On Windows

uv pip install -e ".[dev]"  # Install with development dependencies
```

4. Set up environment variables:
Create a `.env` file in the project root with the following variables:
```env
GITHUB_TOKEN=your_github_token
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_REGION=your_aws_region
```

## Usage

### Generating Commit Messages

Use the commit message generator to create meaningful commit messages:

```bash
python -m git_ai.generate_commit_msg
```

### Generating PR Descriptions

Generate detailed PR descriptions for your pull requests:

```bash
python -m git_ai.generate_pr_description
```

## Development

### Code Style and Quality

- Use `ruff` for linting and formatting
- Follow PEP 8 style guide
- Run tests before submitting PRs

### Testing

Run the test suite:
```bash
pytest
```

For specific test categories:
```bash
pytest -m "not integration"  # Run only unit tests
pytest -m integration       # Run only integration tests
```

## Project Structure

```
.
├── src/
│   └── git_ai/
│       ├── generate_commit_msg.py    # Commit message generator
│       ├── generate_pr_description.py # PR description generator
│       └── __init__.py
├── tests/           # Test files
├── pyproject.toml   # Project configuration and dependencies
├── .envrc          # Environment variables template
└── .gitignore      # Git ignore rules
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request
