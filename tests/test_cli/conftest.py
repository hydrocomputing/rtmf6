"""Pytest fixtures for CLI tests."""

from pathlib import Path

import pytest


@pytest.fixture
def fixtures_path() -> Path:
    """Return path to test fixtures directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def sample_config(fixtures_path) -> Path:
    """Return path to sample rtmf6.toml config file."""
    return fixtures_path / "rtmf6.toml"
