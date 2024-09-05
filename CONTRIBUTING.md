# Contributing Guidelines

This document outlines the contributing guidelines for the Provena client library. Contributions are welcome for new features, bug fixes, and documentation updates.

---

## Usage

### How to get started with Poetry

1) Run the Command: `curl -sSL https://install.python-poetry.org | python3 -`.
2) Check if poetry was successfully installed by running `poetry --version`.
3) You should now have be able to see your poetry version successfully. 
4) Now run the command `poetry shell`. This  will activate the poetry virtual environment for you.
5) Now finally run the command `poetry install`. This will install all dependencies defined within pyproject.toml.

### Using local .venv

1) Set poetry to use local `.venv` with `poetry config virtualenvs.in-project true`
2) List and remove any existing venvs with `poetry env list` and `poetry env remove <name>`
3) Install `poetry install`

You can then make vs code use this environment easily with `ctrl + shift + p` select python interpreter choosing `.venv/bin/python`. 

### My Poetry Installation is not being detected?
1) This means that your PATH variable does not include the Poetry directory. 
2) Open your .bashrc file, using the command `nano ~/.bashrc`.
3) Add the following line at the end of the file, `export PATH= "$HOME/.local/bin:$PATH"`.
4) Reload your .bashrc file, using the command `source ~/.bashrc`.
5) Verify that your poetry is now running, using the command `poetry --version`.


## How to contribute to the Provena Python Client

### 1) Initial Setup

1. **Ensure You Have an IDE Installed**: Start by setting up your preferred Integrated Development Environment (IDE) like VSCode, PyCharm, etc.
2. **Clone the Repository**: Use the following command to clone the Provena client repository locally: `git clone https://github.com/provena/provena-python-client.git `
3. **Install Requirements**: The Provena Python client uses Poetry for dependency management. Install Poetry if it's not already installed, following the steps above. 
4. **Set Up Mypy for Static Type Checking**: Ensure you have Mypy configured to check for type errors. You can run Mypy manually: `poetry run mypy` or `python run mypy` if using local .venv

### 2) Codebase Layout and Contributing

Before making any contributions, it's important to understand the core structure of the Provena Python Client.

- **Core Directory Layout**:

    - **docs**: All documentation is located here and should be updated if your contribution involves documentation changes or additions.
    - **src/provenaclient**: This directory contains the core functionality of the Provena client. Any new features, bug fixes, or changes to the core logic should be made here.
    - **tests**: All unit and integration tests are located in this directory. If your contribution involves code changes or new features, corresponding tests should be written or updated here.
    
- **Where to Add New Features**:

    - Any new feature should be added within the `src/provenaclient/` directory, following the existing architecture structure and file organisation.
    - If you are extending or updating an existing feature or API endpoint, locate the relevant module and update the code accordingly to ensure consistency with the existing architecture.

- **Adding Tests**:

    - All new features or bug fixes may include corresponding tests in the `tests` directory if appropriate.
    - Use Pytest for writing unit or integration tests to ensure that the new functionality is properly covered.
    - If you're adding new test cases, ensure they are comprehensive and maintain test coverage for the affected code.

- **Code Style**:

    - Maintain consistency with the existing codebase in terms of structure, style, and naming conventions.
    - Use docstrings to document functions, classes, and modules where necessary, ensuring the code is well-documented for future contributors.
    - Ensure that all functions and methods are properly typed for static type checking, and use Mypy to validate the typing.


### 3) Create a New Branch

Name your branch descriptively, e.g., `<change scope:feat|fix|docs>-<jira-ticket-name>`.

### 4) Commit Message Conventions

We follow the [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) specification for commit messages. This helps automate the versioning and release process.

- Conventional Commits Examples:

    - **feat:** A new feature.
    - **fix:** A bug fix.
    - **chore:** Changes to the build process or auxiliary tools and libraries.
    - **docs:** Documentation only changes.
    - **style:** Changes that do not affect the meaning of the code (white-space, formatting, missing semi-colons, etc).
    - **refactor:** A code change that neither fixes a bug nor adds a feature.
    - **perf:** A code change that improves performance.
    - **test:** Adding missing tests or correcting existing tests.

**Note:** Commits with types of `docs`, `chore`, `style`, `refactor`, and `test` will not trigger a version change.

### 5) Develop and Commit

- Make your desired changes in your branch.
- Commit your changes to your upstream branch and use meaningful commit messages.

### 6) Open a Pull Request (PR)

- When your feature is complete, open a PR to the main branch.
- Ensure that your PR title adheres and begins by one of the Conventional Commits specification keywords outlined above.
- Ensure your PR description is clear and outlines the changes made.
- Ensure that the CI (Continuous Integration) has successfully passed for your latest commit.

### 7) Review and Squash Merge

- Request reviews from at least one team member within the Provena organisation or part of the client library development.
- Once approved, squash merge the PR into main with a specific commit message that summarises the changes, e.g., `feat: added new endpoint in job-api` or re-use the PR title.

### 8) CI/CD Flow

After merging, the CI/CD pipeline will run automatically, deploying the changes and updating the version as needed.


## Provena Client CI/CD and Release Process

## Overview

The Provena client uses GitHub Actions for CI/CD, producing automated deployments to our [PyPI account](https://pypi.org/project/provenaclient/).

## Continuous Integration (CI)

**Executed:** Creation of pull requests and during merge of pull requests to the main branch.

**Triggers:** Push and pull requests to the main branch.

**Steps:**
1. Set up Python environment.
2. Check out the repository.
3. Install dependencies with Poetry.
4. Run type checks with Mypy.
5. Run tests with Pytest (unit tests, integration tests).
6. Track coverage with Codecov.
7. Build documentation.

## Continuous Deployment (CD)

**Executed:** Merge of pull requests to the main branch.

**Triggers:** Push to the main branch and merged pull requests to the main branch.

**Steps:**
1. Set up Python environment.
2. Check out repository.
3. Use `python-semantic-release` to prepare release.
4. Publish to TestPyPI and PyPI.
5. Test install from TestPyPI.
6. Upload distributions to GitHub Releases.

## Semantic Versioning and Release Automation

The Provena Client uses `python-semantic-release` for automated versioning and releases.

### Configuration in `pyproject.toml` `[tool.semantic_release]`

- **Version Management:** Package versions are managed through `pyproject.toml` and `src/provenaclient/__init__.py`.
- **Release Branch:** Releases of the Provena Client are made from the main branch only.
- **Changelog:** Release changelog and commit documentation/history is maintained in `CHANGELOG.md`.
- **Upload to PyPI and GitHub Releases:** Set to true.
- **Automatic Version Commit:** `commit_version_number = true` ensures that the version number is automatically committed back to the repository after a release, keeping the `pyproject.toml` and `src/provenaclient/__init__.py` files up to date.

## Release Process

On merging to the main branch, `python-semantic-release` automates the following steps:

### Bumps the Version

Based on commit messages, the version is incremented following semantic versioning rules:

- **feat:** Increments the MINOR version.
- **fix:** Increments the PATCH version.
- **BREAKING CHANGE:** Increments the MAJOR version.

### Creates a New Tag

A new Git tag is created for the version.

### Publishes to PyPI

The new version is published to PyPI.

### Uploads to GitHub Releases

The distribution files are uploaded to GitHub Releases.

### Commits the New Version Number

The new version number is committed back to the repository, ensuring the `pyproject.toml` and `src/provenaclient/__init__.py` files are up-to-date.

## Overall Summary

This setup ensures a streamlined and automated release process for the Provena Client, with CI/CD pipelines handling testing and deployment, and `python-semantic-release` managing semantic versioning and PyPI releases.

## License

`provenaclient` was created by Provena Development Team (CSIRO). Provena Development Team (CSIRO) retains all rights to the source and it may not be reproduced, distributed, or used to create derivative works.

## Credits

`provenaclient` was created with [`cookiecutter`](https://cookiecutter.readthedocs.io/en/latest/) and the `py-pkgs-cookiecutter` [template](https://github.com/py-pkgs/py-pkgs-cookiecutter).