"""
Pytest configuration and shared fixtures for ExoHunter Pro test suite.

This module provides:
- Shared fixtures for test setup/teardown
- Temporary test files and directories
- Pre-configured test instances
"""

import json
import shutil
from pathlib import Path

import pytest

from exohunter import ExoHunter
from issue_tracker import IssueTracker


@pytest.fixture
def tmp_path(tmp_path):
    """
    Override default tmp_path to ensure clean working directory.
    
    This fixture provides a temporary directory that is cleaned up
    after each test function.
    """
    return tmp_path


@pytest.fixture
def default_config(tmp_path):
    """
    Create a default config.json in the temporary directory.
    
    Returns:
        Path: Path to the created config file.
    """
    config_data = {
        "max_targets": 10,
        "difficulty_levels": ["easy", "medium", "hard"],
        "score_thresholds": {"easy": 100, "medium": 250, "hard": 500},
        "sectors": ["alpha", "beta", "gamma", "delta", "epsilon"],
        "game_settings": {
            "target_spawn_rate": 0.7,
            "bonus_round_enabled": True,
            "leaderboard_enabled": True
        },
        "version": "1.0.0"
    }
    
    config_file = tmp_path / "config.json"
    with open(config_file, "w") as f:
        json.dump(config_data, f, indent=2)
    
    # Change to tmp_path so default config.json is found
    original_cwd = Path.cwd()
    import os
    os.chdir(tmp_path)
    
    yield config_file
    
    os.chdir(original_cwd)


@pytest.fixture
def custom_config_file(tmp_path):
    """
    Create a custom config file for testing configuration overrides.
    
    Returns:
        Path: Path to the custom config file.
    """
    config_data = {
        "max_targets": 5,
        "difficulty_levels": ["easy", "medium", "hard", "expert"],
        "score_thresholds": {"easy": 50, "medium": 150, "hard": 300, "expert": 1000},
        "sectors": ["alpha", "beta", "custom_sector"],
        "custom_setting": "test_value",
        "version": "2.0.0-test"
    }
    
    config_file = tmp_path / "custom_config.json"
    with open(config_file, "w") as f:
        json.dump(config_data, f, indent=2)
    
    return config_file


@pytest.fixture
def hunter_instance(tmp_path, default_config):
    """
    Create a fresh ExoHunter instance for testing.
    
    This fixture ensures each test gets a clean ExoHunter instance
    with a temporary config file.
    
    Returns:
        ExoHunter: A new ExoHunter instance.
    """
    import os
    original_cwd = Path.cwd()
    os.chdir(tmp_path)
    
    hunter = ExoHunter()
    
    yield hunter
    
    os.chdir(original_cwd)


@pytest.fixture
def tracker_instance(tmp_path):
    """
    Create a fresh IssueTracker instance for testing.
    
    This fixture ensures each test gets a clean IssueTracker instance
    with a temporary issues file.
    
    Returns:
        IssueTracker: A new IssueTracker instance.
    """
    issues_file = tmp_path / "test_issues.json"
    tracker = IssueTracker(issues_path=str(issues_file))
    
    yield tracker
    
    # Cleanup
    if issues_file.exists():
        issues_file.unlink()
    
    log_path = Path("issues_log.json")
    if log_path.exists() and tmp_path in log_path.resolve().parents:
        log_path.unlink()


@pytest.fixture
def issues_file(tmp_path):
    """
    Create a pre-populated issues.json file for testing.
    
    Returns:
        Path: Path to the issues file with sample data.
    """
    issues_data = [
        {
            "number": 1,
            "title": "First Issue",
            "body": "This is the first test issue",
            "labels": ["bug", "high-priority"],
            "state": "open",
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-01T00:00:00"
        },
        {
            "number": 2,
            "title": "Second Issue",
            "body": "This is the second test issue",
            "labels": ["enhancement"],
            "state": "open",
            "created_at": "2024-01-02T00:00:00",
            "updated_at": "2024-01-02T00:00:00"
        }
    ]
    
    issues_file = tmp_path / "issues.json"
    with open(issues_file, "w") as f:
        json.dump(issues_data, f, indent=2)
    
    return issues_file


@pytest.fixture
def project_files(tmp_path):
    """
    Create sample project files for repository verification tests.
    
    Returns:
        list: List of created file paths.
    """
    import os
    original_cwd = Path.cwd()
    os.chdir(tmp_path)
    
    files = []
    
    # Create Python files
    exohunter_py = tmp_path / "exohunter.py"
    exohunter_py.write_text("# ExoHunter main module\n")
    files.append(exohunter_py)
    
    issue_tracker_py = tmp_path / "issue_tracker.py"
    issue_tracker_py.write_text("# Issue Tracker module\n")
    files.append(issue_tracker_py)
    
    # Create config file
    config_json = tmp_path / "config.json"
    config_json.write_text('{"test": true}')
    files.append(config_json)
    
    # Create README
    readme_md = tmp_path / "README.md"
    readme_md.write_text("# Test Project\n")
    files.append(readme_md)
    
    yield files
    
    os.chdir(original_cwd)


@pytest.fixture
def populated_tracker(tmp_path, issues_file):
    """
    Create an IssueTracker with pre-populated issues.
    
    Returns:
        IssueTracker: A tracker with sample issues loaded.
    """
    tracker = IssueTracker(issues_path=str(issues_file))
    return tracker


@pytest.fixture
def clean_log_file(tmp_path):
    """
    Ensure a clean issues_log.json for testing.
    
    This fixture removes any existing log file before the test
    and cleans up after.
    
    Returns:
        Path: Path to the log file location.
    """
    import os
    original_cwd = Path.cwd()
    os.chdir(tmp_path)
    
    log_path = tmp_path / "issues_log.json"
    
    # Remove if exists
    if log_path.exists():
        log_path.unlink()
    
    yield log_path
    
    # Cleanup
    if log_path.exists():
        log_path.unlink()
    
    os.chdir(original_cwd)


@pytest.fixture
def sample_hunt_data():
    """
    Provide sample hunt data for testing.
    
    Returns:
        dict: Sample hunt result data.
    """
    return {
        "target_ids": ["TGT-001", "TGT-002", "TGT-003"],
        "sectors": ["alpha", "beta", "gamma", "delta"],
        "difficulties": ["easy", "medium", "hard"],
        "base_points": [50, 75, 100, 125, 150],
        "multipliers": {"easy": 1.0, "medium": 1.5, "hard": 2.5}
    }


@pytest.fixture
def sample_issue_data():
    """
    Provide sample issue data for testing.
    
    Returns:
        dict: Sample issue data.
    """
    return {
        "titles": ["Bug Fix", "Feature Request", "Documentation Update"],
        "bodies": ["This needs to be fixed", "Please add this feature", "Docs need updating"],
        "labels": ["bug", "enhancement", "documentation", "help wanted", "good first issue"]
    }


# Parametrized fixtures for comprehensive testing

@pytest.fixture(params=["easy", "medium", "hard"])
def difficulty_level(request):
    """
    Parametrized fixture for testing different difficulty levels.
    
    Usage:
        def test_something(difficulty_level):
            # Test runs with easy, medium, and hard
    """
    return request.param


@pytest.fixture(params=["alpha", "beta", "gamma", "delta"])
def valid_sector(request):
    """
    Parametrized fixture for testing different valid sectors.
    
    Usage:
        def test_sector_tracking(valid_sector):
            # Test runs with each valid sector
    """
    return request.param


@pytest.fixture(params=["invalid", "xyz", "", "123"])
def invalid_sector(request):
    """
    Parametrized fixture for testing invalid sectors.
    
    Usage:
        def test_invalid_sector(invalid_sector):
            # Test runs with each invalid sector
    """
    return request.param


@pytest.fixture(params=[
    {"title": "Short", "body": "A"},
    {"title": "Medium" * 10, "body": "Body" * 50},
    {"title": "Long" * 100, "body": "Content" * 500},
])
def issue_variations(request):
    """
    Parametrized fixture for testing issues with different sizes.
    
    Usage:
        def test_issue_creation(issue_variations, tracker_instance):
            tracker_instance.create_issue(**issue_variations)
    """
    return request.param
