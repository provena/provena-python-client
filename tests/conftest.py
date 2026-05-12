"""Pytest hooks and shared helpers for this package's tests."""

from __future__ import annotations

import os

import pytest


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--skip-integration-user-person-link",
        action="store_true",
        default=False,
        help=(
            "Integration tests only: skip auth user–person link assign/clear in "
            "org_person_fixture (dataset mint may require linking outside tests)."
        ),
    )


@pytest.fixture(scope="session")
def integration_skip_user_person_link(request: pytest.FixtureRequest) -> bool:
    """True when CLI flag or env opts out of user–person link steps in integration tests."""
    if request.config.getoption("--skip-integration-user-person-link"):
        return True
    v = os.getenv("PROVENA_SKIP_INTEGRATION_USER_PERSON_LINK", "").strip().lower()
    return v in ("1", "true", "yes", "on")
