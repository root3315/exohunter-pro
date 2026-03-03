"""
Comprehensive unit tests for ExoHunter Pro - exohunter.py module.

Tests cover:
- Initialization and configuration loading
- Core gameplay mechanics (hunt, track_target)
- Difficulty management
- Status and repository verification
- Issue activity logging
- Edge cases and error handling
"""

import json
import random
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from exohunter import ExoHunter
from issue_tracker import IssueTracker


class TestExoHunterInitialization:
    """Tests for ExoHunter initialization and configuration."""

    def test_init_with_default_config(self, default_config):
        """Test initialization with default config.json."""
        hunter = ExoHunter()
        assert hunter.config_path == Path("config.json")
        assert hunter.score == 0
        assert hunter.current_difficulty == "easy"
        assert hunter.targets_hunted == 0
        assert hunter.active_target is None
        assert isinstance(hunter.issue_tracker, IssueTracker)

    def test_init_with_custom_config(self, custom_config_file):
        """Test initialization with custom config path."""
        hunter = ExoHunter(config_path=str(custom_config_file))
        assert hunter.config_path == custom_config_file
        assert hunter.config["max_targets"] == 5
        assert hunter.config["custom_setting"] == "test_value"

    def test_init_with_nonexistent_config(self, tmp_path):
        """Test initialization with non-existent config file uses defaults."""
        nonexistent = tmp_path / "nonexistent.json"
        hunter = ExoHunter(config_path=str(nonexistent))
        assert hunter.config == {
            "max_targets": 10,
            "difficulty_levels": ["easy", "medium", "hard"],
            "score_thresholds": {"easy": 100, "medium": 250, "hard": 500},
        }

    def test_load_config_from_file(self, default_config):
        """Test loading configuration from existing file."""
        hunter = ExoHunter()
        assert "max_targets" in hunter.config
        assert "difficulty_levels" in hunter.config
        assert "sectors" in hunter.config


class TestHuntMethod:
    """Tests for the hunt method."""

    def test_hunt_success(self, hunter_instance):
        """Test successful hunt operation."""
        with patch.object(hunter_instance, '_get_base_points', return_value=100):
            result = hunter_instance.hunt("TGT-001")
        
        assert result["status"] == "success"
        assert result["target_id"] == "TGT-001"
        assert result["points"] == 100  # 100 * 1.0 (easy multiplier)
        assert result["total_score"] == 100
        assert hunter_instance.targets_hunted == 1

    def test_hunt_with_difficulty_multiplier(self, hunter_instance):
        """Test hunt with different difficulty multipliers."""
        hunter_instance.set_difficulty("medium")
        with patch.object(hunter_instance, '_get_base_points', return_value=100):
            result = hunter_instance.hunt("TGT-002")
        
        assert result["points"] == 150  # 100 * 1.5 (medium multiplier)

    def test_hunt_hard_difficulty(self, hunter_instance):
        """Test hunt with hard difficulty."""
        hunter_instance.set_difficulty("hard")
        with patch.object(hunter_instance, '_get_base_points', return_value=100):
            result = hunter_instance.hunt("TGT-003")
        
        assert result["points"] == 250  # 100 * 2.5 (hard multiplier)

    def test_hunt_max_targets_reached(self, hunter_instance):
        """Test hunt fails when max targets reached."""
        hunter_instance.targets_hunted = 10  # Set to max
        result = hunter_instance.hunt("TGT-004")
        
        assert result["status"] == "failed"
        assert result["reason"] == "Maximum targets reached"
        assert result["points"] == 0
        assert hunter_instance.score == 0  # Score unchanged

    def test_hunt_accumulates_score(self, hunter_instance):
        """Test that multiple hunts accumulate score."""
        with patch.object(hunter_instance, '_get_base_points', return_value=50):
            result1 = hunter_instance.hunt("TGT-005")
            result2 = hunter_instance.hunt("TGT-006")
        
        assert result1["total_score"] == 50
        assert result2["total_score"] == 100
        assert hunter_instance.targets_hunted == 2

    def test_hunt_custom_max_targets(self, custom_config_file):
        """Test hunt respects custom max_targets from config."""
        hunter = ExoHunter(config_path=str(custom_config_file))
        
        with patch.object(hunter, '_get_base_points', return_value=50):
            for i in range(5):
                result = hunter.hunt(f"TGT-{i}")
                assert result["status"] == "success"
            
            # 6th hunt should fail
            result = hunter.hunt("TGT-007")
            assert result["status"] == "failed"
            assert result["reason"] == "Maximum targets reached"


class TestTrackTargetMethod:
    """Tests for the track_target method."""

    def test_track_target_valid_sector_found(self, hunter_instance):
        """Test tracking target in valid sector with target found."""
        with patch('random.random', return_value=0.8):  # > 0.3 means found
            result = hunter_instance.track_target("alpha")
        
        assert result["found"] is True
        assert "target" in result
        assert result["target"]["sector"] == "alpha"
        assert result["target"]["difficulty"] == "easy"
        assert "id" in result["target"]

    def test_track_target_valid_sector_not_found(self, hunter_instance):
        """Test tracking target in valid sector but no target found."""
        with patch('random.random', return_value=0.1):  # <= 0.3 means not found
            result = hunter_instance.track_target("beta")
        
        assert result["found"] is False
        assert "No targets detected" in result["message"]

    def test_track_target_invalid_sector(self, hunter_instance):
        """Test tracking target in invalid sector."""
        result = hunter_instance.track_target("invalid_sector")
        
        assert result["found"] is False
        assert "Invalid sector" in result["message"]

    def test_track_target_case_insensitive(self, hunter_instance):
        """Test sector matching is case insensitive."""
        with patch('random.random', return_value=0.8):
            result = hunter_instance.track_target("ALPHA")
        
        assert result["found"] is True
        assert result["target"]["sector"] == "ALPHA"

    def test_track_target_all_valid_sectors(self, hunter_instance):
        """Test tracking in all valid sectors."""
        valid_sectors = ["alpha", "beta", "gamma", "delta"]
        
        for sector in valid_sectors:
            with patch('random.random', return_value=0.8):
                result = hunter_instance.track_target(sector)
            assert result["found"] is True

    def test_track_target_sets_active_target(self, hunter_instance):
        """Test that tracking sets the active_target attribute."""
        with patch('random.random', return_value=0.8):
            hunter_instance.track_target("gamma")
        
        assert hunter_instance.active_target is not None
        assert hunter_instance.active_target["sector"] == "gamma"


class TestDifficultyManagement:
    """Tests for difficulty level management."""

    def test_set_difficulty_valid_levels(self, hunter_instance):
        """Test setting valid difficulty levels."""
        assert hunter_instance.set_difficulty("easy") is True
        assert hunter_instance.current_difficulty == "easy"
        
        assert hunter_instance.set_difficulty("medium") is True
        assert hunter_instance.current_difficulty == "medium"
        
        assert hunter_instance.set_difficulty("hard") is True
        assert hunter_instance.current_difficulty == "hard"

    def test_set_difficulty_case_insensitive(self, hunter_instance):
        """Test difficulty setting is case insensitive."""
        assert hunter_instance.set_difficulty("MEDIUM") is True
        assert hunter_instance.current_difficulty == "medium"
        
        assert hunter_instance.set_difficulty("HaRd") is True
        assert hunter_instance.current_difficulty == "hard"

    def test_set_difficulty_invalid_level(self, hunter_instance):
        """Test setting invalid difficulty level."""
        result = hunter_instance.set_difficulty("extreme")
        assert result is False
        assert hunter_instance.current_difficulty == "easy"  # Unchanged

    def test_set_difficulty_empty_string(self, hunter_instance):
        """Test setting empty string as difficulty."""
        result = hunter_instance.set_difficulty("")
        assert result is False

    def test_get_difficulty_multiplier_all_levels(self, hunter_instance):
        """Test difficulty multipliers for all levels."""
        multipliers = {"easy": 1.0, "medium": 1.5, "hard": 2.5}
        
        for level, expected in multipliers.items():
            hunter_instance.current_difficulty = level
            assert hunter_instance._get_difficulty_multiplier() == expected

    def test_get_difficulty_multiplier_default(self, hunter_instance):
        """Test default multiplier for unknown difficulty."""
        hunter_instance.current_difficulty = "unknown"
        assert hunter_instance._get_difficulty_multiplier() == 1.0


class TestGetStatusMethod:
    """Tests for the get_status method."""

    def test_get_status_initial_state(self, hunter_instance):
        """Test status at initial state."""
        status = hunter_instance.get_status()
        
        assert status["score"] == 0
        assert status["targets_hunted"] == 0
        assert status["max_targets"] == 10
        assert status["difficulty"] == "easy"
        assert status["active_target"] is None

    def test_get_status_after_hunts(self, hunter_instance):
        """Test status after multiple hunts."""
        with patch.object(hunter_instance, '_get_base_points', return_value=100):
            hunter_instance.hunt("TGT-001")
            hunter_instance.hunt("TGT-002")
        
        status = hunter_instance.get_status()
        assert status["score"] == 200
        assert status["targets_hunted"] == 2

    def test_get_status_with_active_target(self, hunter_instance):
        """Test status with active target."""
        with patch('random.random', return_value=0.8):
            hunter_instance.track_target("delta")
        
        status = hunter_instance.get_status()
        assert status["active_target"] is not None
        assert status["active_target"]["sector"] == "delta"


class TestRepositoryVerification:
    """Tests for repository verification methods."""

    def test_get_repository_files_finds_files(self, hunter_instance, project_files):
        """Test that get_repository_files finds project files."""
        files = hunter_instance.get_repository_files()
        
        assert len(files) > 0
        assert any("exohunter.py" in f for f in files)
        assert any("issue_tracker.py" in f for f in files)

    def test_verify_repository_valid(self, hunter_instance, project_files):
        """Test verify_repository returns valid status."""
        result = hunter_instance.verify_repository()
        
        assert result["is_empty"] is False
        assert result["file_count"] > 0
        assert result["status"] == "valid"
        assert result["config_exists"] is True

    def test_verify_repository_config_exists(self, hunter_instance):
        """Test that config existence is checked."""
        result = hunter_instance.verify_repository()
        assert "config_exists" in result


class TestIssueActivityLogging:
    """Tests for issue activity logging."""

    def test_log_issue_activity_ai_request(self, hunter_instance, tmp_path):
        """Test logging AI request activity."""
        log_path = tmp_path / "issues_log.json"
        original_path = hunter_instance.issue_tracker.issues_path
        
        with patch.object(hunter_instance.issue_tracker, 'issues_path', log_path):
            result = hunter_instance.log_issue_activity(
                issue_number=1,
                activity_type="ai_request",
                label="test-label"
            )
        
        assert result["type"] == "ai_request"
        assert result["issue_number"] == 1
        assert result["label"] == "test-label"

    def test_log_issue_activity_ai_response(self, hunter_instance, tmp_path):
        """Test logging AI response activity."""
        log_path = tmp_path / "issues_log.json"
        
        with patch.object(hunter_instance.issue_tracker, 'issues_path', log_path):
            result = hunter_instance.log_issue_activity(
                issue_number=2,
                activity_type="ai_response",
                label="response-label",
                details={"response_len": 500, "first_line": "Test response"}
            )
        
        assert result["type"] == "ai_response"
        assert result["issue_number"] == 2
        assert result["response_len"] == 500
        assert result["first_line"] == "Test response"

    def test_log_issue_activity_invalid_type(self, hunter_instance):
        """Test logging with invalid activity type."""
        result = hunter_instance.log_issue_activity(
            issue_number=1,
            activity_type="invalid_type",
            label="test"
        )
        
        assert "error" in result
        assert result["error"] == "Invalid activity type"

    def test_log_issue_activity_with_empty_details(self, hunter_instance, tmp_path):
        """Test logging AI response with empty details."""
        log_path = tmp_path / "issues_log.json"
        
        with patch.object(hunter_instance.issue_tracker, 'issues_path', log_path):
            result = hunter_instance.log_issue_activity(
                issue_number=3,
                activity_type="ai_response",
                label="test",
                details=None
            )
        
        assert result["response_len"] == 0
        assert result["first_line"] == ""


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_hunt_with_empty_target_id(self, hunter_instance):
        """Test hunt with empty target ID."""
        with patch.object(hunter_instance, '_get_base_points', return_value=50):
            result = hunter_instance.hunt("")
        
        assert result["status"] == "success"
        assert result["target_id"] == ""

    def test_hunt_with_special_characters_in_target_id(self, hunter_instance):
        """Test hunt with special characters in target ID."""
        with patch.object(hunter_instance, '_get_base_points', return_value=50):
            result = hunter_instance.hunt("TGT-@#$%^&*()")
        
        assert result["status"] == "success"
        assert result["target_id"] == "TGT-@#$%^&*()"

    def test_track_target_with_special_characters(self, hunter_instance):
        """Test tracking with special characters in sector name."""
        result = hunter_instance.track_target("alpha@beta")
        assert result["found"] is False

    def test_track_target_with_unicode(self, hunter_instance):
        """Test tracking with unicode characters."""
        result = hunter_instance.track_target("αlpha")
        assert result["found"] is False

    def test_set_difficulty_with_whitespace(self, hunter_instance):
        """Test setting difficulty with whitespace."""
        result = hunter_instance.set_difficulty("  medium  ")
        assert result is False  # Whitespace not trimmed, should fail

    def test_get_status_immutability(self, hunter_instance):
        """Test that get_status returns a copy, not internal state."""
        status = hunter_instance.get_status()
        status["score"] = 9999
        assert hunter_instance.get_status()["score"] == 0

    def test_multiple_track_target_calls(self, hunter_instance):
        """Test multiple track_target calls update active_target."""
        with patch('random.random', return_value=0.8):
            hunter_instance.track_target("alpha")
            first_target = hunter_instance.active_target
            
            hunter_instance.track_target("beta")
            second_target = hunter_instance.active_target
        
        assert first_target["sector"] == "alpha"
        assert second_target["sector"] == "beta"

    def test_hunt_at_exact_max_limit(self, hunter_instance):
        """Test hunt behavior at exact max targets limit."""
        hunter_instance.targets_hunted = 9
        
        with patch.object(hunter_instance, '_get_base_points', return_value=50):
            result = hunter_instance.hunt("TGT-LAST")
        
        assert result["status"] == "success"
        assert hunter_instance.targets_hunted == 10
        
        # Next hunt should fail
        result = hunter_instance.hunt("TGT-OVER")
        assert result["status"] == "failed"


class TestConfigurationOverrides:
    """Tests for configuration file overrides."""

    def test_custom_sectors_from_config(self, custom_config_file):
        """Test that custom sectors are loaded from config."""
        hunter = ExoHunter(config_path=str(custom_config_file))
        assert "custom_sector" in hunter.config.get("sectors", [])

    def test_custom_difficulty_levels_from_config(self, custom_config_file):
        """Test custom difficulty levels from config."""
        hunter = ExoHunter(config_path=str(custom_config_file))
        assert "expert" in hunter.config.get("difficulty_levels", [])

    def test_score_thresholds_from_config(self, default_config):
        """Test score thresholds are loaded correctly."""
        hunter = ExoHunter()
        thresholds = hunter.config.get("score_thresholds", {})
        assert thresholds["easy"] == 100
        assert thresholds["medium"] == 250
        assert thresholds["hard"] == 500
