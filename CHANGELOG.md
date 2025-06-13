# CHANGELOG


## v0.0.0 (2025-06-13)

### Unknown

* **build:** Update project description, raise Python version, and adjust dependencies

- Updated project description for broader AI applications with git history.
- Raised the Python requirement to version 3.11 for compatibility.
- Updated development dependencies by including `python-semantic-release` instead of version-specific ones.
- Added configuration for `semantic_release` to manage version from `pyproject.toml`.
- Added new packages like `boto3`, `botocore`, `cffi`, and `click-option-group` in `uv.lock`. ([`34b5e1e`](https://github.com/timfurlong/git-ai/commit/34b5e1e0bf8b9aaf024a129d36346cd2cdf2df4d))

* **docs:** Update README to reflect switch from AWS Bedrock to LiteLLM

- Modified references to AWS Bedrock with LiteLLM, highlighting the default use of GPT-4 for AI capabilities.
- Updated prerequisites to remove AWS account requirements.
- Added a link to LiteLLM documentation for AI model configuration details.
- Adjusted `.env` file instructions to exclude AWS environment variables. ([`923cbdb`](https://github.com/timfurlong/git-ai/commit/923cbdb3d5418fe5140febaa449a60e710299201))

* **docs:** Update README with enhanced features and setup process

- Expanded the README to detail new features, including AI-based commit message and PR description generation.
- Updated prerequisites section to include necessary Python, GitHub, and AWS configurations.
- Enhanced installation instructions with comprehensive step-by-step guidance.
- Introduced usage examples for generating commit messages and PR descriptions.
- Provided guidelines for code style, linting, and testing using `ruff`, `black`, and `pytest`.

**chore:** Remove deprecated `generate_pr_description.py`

- Deleted `generate_pr_description.py` as its functionality is now integrated elsewhere or obsolete.
- Adjusted documentation and project references to omit the removed script. ([`d781d2e`](https://github.com/timfurlong/git-ai/commit/d781d2ecdd0d8bf4565df00b14bd489ff6c81572))

* **refactor:** Restructure project and update imports for `generate_commit_msg`

- Moved `generate_commit_msg.py` to `src/git_ai/` for better project structure.
- Deleted `test_bedrock.py` as it's no longer needed.
- Updated import paths in `tests/test_generate_commit_msg.py` to align with new file location.
- Ensured all test cases and mocks reflect the updated import paths. ([`3062cb2`](https://github.com/timfurlong/git-ai/commit/3062cb26fc1f8fd76d840796d471efed1381331d))

* **refactor:** Migrate from Bedrock to LiteLLM for PR description generation

- Switched from `instructor` and `boto3` to `litellm` for PR description generation in `generate_pr_description.py`.
- Updated environment configuration to support LiteLLM model selection.
- Enhanced error handling for JSON parsing in API responses.
- Updated existing tests in `test_generate_pr_description.py` to align with changes, utilizing `pytest-mock` for mocking.
- Added integration tests in `test_generate_pr_description_integration.py` with optional execution controlled by `INTEGRATION_TESTS` environment variable.
- Enhanced `pyproject.toml` with custom pytest markers for integration tests. ([`a9f1089`](https://github.com/timfurlong/git-ai/commit/a9f10890031277f944c00276718c3be1458f0b0b))

* **feat:** Implement AI-powered PR description generation with Bedrock

- Updated `pyproject.toml` to reflect changes in project dependencies and Python version.
- Introduced new module `generate_pr_description.py` utilizing Bedrock for generating GitHub PR descriptions.
- Updated `__init__.py` to export new functionalities.
- Added `test_bedrock.py` as a standalone script for testing PR description generation.
- Created comprehensive test suite in `tests/test_generate_pr_description.py` to ensure functionality and error handling.
- Required AWS setup for Bedrock client and proper GitHub token handling. ([`858a47a`](https://github.com/timfurlong/git-ai/commit/858a47abac8687c077740d126047ff60d324febf))

* **refactor:** Simplify test mocking with pytest-mock and update dev dependencies

- Replace `unittest.mock` with `pytest-mock` for cleaner mocking in `test_generate_commit_msg.py`.
- Add `pytest-mock==3.14.0` to dev dependencies in `pyproject.toml`.
- Refactor test cases to use `mocker` for consistent API response mocking. ([`4b81495`](https://github.com/timfurlong/git-ai/commit/4b8149541c0abee413b53524913ebaecb9534549))

* Add interactive commit message generation with user feedback loop including test cases ([`908343b`](https://github.com/timfurlong/git-ai/commit/908343b14fefd5feecbaff79af47acae96cf7f4b))

* **feat:** Enhance commit message generation with previous commit integration

- Added `get_previous_commit_messages` to retrieve past commit messages for style consistency.
- Updated `generate_commit_msg` to optionally include previous commit messages in the prompt.
- Added `--no-previous` flag to CLI to exclude previous commit messages if desired.
- Extended test suite with tests for retrieving previous commit messages and scenarios with/without including them in the generation process. ([`14843ed`](https://github.com/timfurlong/git-ai/commit/14843edbb00d03c0b1cb599d4e26e9da8386078a))

* Add argparse support for additional prompt context in commit message generation script and update test cases to cover new functionality. ([`3114b83`](https://github.com/timfurlong/git-ai/commit/3114b83d69eb0cb0036f114361704e8e66379f0c))

* **feat:** Implement commit message generation functionality

- Added a new function `generate_commit_msg` to `generate_commit_msg.py` to generate commit messages using the `litellm` API. The function formats the file diffs and constructs a prompt for the model, then returns the model's response.
- Updated the main section in `generate_commit_msg.py` to use `generate_commit_msg` for generating commit messages from the output of `smart_diff`.
- Expanded the test suite in `test_generate_commit_msg.py`:
  - Added unit tests for `generate_commit_msg` with mocked API responses.
  - Tests include scenarios for generating messages with single file changes, multiple file changes, and no changes. ([`662c1b4`](https://github.com/timfurlong/git-ai/commit/662c1b48015992657e6194cf6b00fd27de7d6734))

* Update dependencies in pyproject.toml to include gitpython and litellm ([`35b0c59`](https://github.com/timfurlong/git-ai/commit/35b0c5914ce184c4902f21f794438ede7726ae0a))

* 3.11 ([`d694c8d`](https://github.com/timfurlong/git-ai/commit/d694c8d7e8d7209d953414a7c535fc60645a5a36))

* init commit ([`996bf99`](https://github.com/timfurlong/git-ai/commit/996bf99f34a02540c363b4562658b06be4ce03ba))
