"""Tests for suivi module."""

from src.modules.suivi.store import ensure_data_dir


def test_ensure_data_dir() -> None:
    """Test data directory creation."""
    ensure_data_dir()
    # If no exception is raised, the test passes
    assert True
