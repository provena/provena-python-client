# provenaclient

A client library for interfacing with a Provena instance.

## Installation

```bash
$ pip install provenaclient
```

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


# Provena Client CI/CD and Release Process

## Overview

The Provena client uses GitHub Actions for CI/CD, producing automated deployments to our PyPI account.

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

### Commit Message Conventions

Follow the Conventional Commits specification. Examples:

- **feat:** A new feature.
- **fix:** A bug fix.
- **chore:** Changes to the build process or auxiliary tools and libraries.
- **docs:** Documentation only changes.
- **style:** Changes that do not affect the meaning of the code (white-space, formatting, missing semi-colons, etc).
- **refactor:** A code change that neither fixes a bug nor adds a feature.
- **perf:** A code change that improves performance.
- **test:** Adding missing tests or correcting existing tests.

**Note:** Commits with types of `docs`, `chore`, `style`, `refactor`, and `test` will not trigger a version change.

More information can be found here: [Conventional Commits Specification](https://www.conventionalcommits.org/en/v1.0.0/).

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

## Best Practices for Adding New Features or Making Changes

### Create a New Branch

Name your branch descriptively, e.g., `<change scope:feat|fix|docs>-<jira-ticket-name>`.

### Develop and Commit

- Make changes in your branch.
- Use meaningful commit messages following the Conventional Commits specification.

### Open a Pull Request (PR)

- When your feature is complete, open a PR to the main branch.
- Ensure that your PR title adheres to the Conventional Commits specification.
- Ensure your PR description is clear and outlines the changes made.
- Ensure that the CI (Continuous Integration) has successfully passed for your latest commit.

### Review and Squash Merge

- Request reviews from at least one team member within the Provena organization and part of the client library development.
- Once approved, squash merge the PR into main with a specific commit message that summarizes the changes, e.g., `feat: added new endpoint in job-api` or re-use the PR title.

### CI/CD Flow

After merging, the CI/CD pipeline will run automatically, deploying the changes and updating the version as needed.

## Overall Summary

This setup ensures a streamlined and automated release process for the Provena Client, with CI/CD pipelines handling testing and deployment, and `python-semantic-release` managing semantic versioning and PyPI releases.



## Contributing
TODO

## License

`provenaclient` was created by Provena Development Team (CSIRO). Provena Development Team (CSIRO) retains all rights to the source and it may not be reproduced, distributed, or used to create derivative works.

## Credits

`provenaclient` was created with [`cookiecutter`](https://cookiecutter.readthedocs.io/en/latest/) and the `py-pkgs-cookiecutter` [template](https://github.com/py-pkgs/py-pkgs-cookiecutter).
