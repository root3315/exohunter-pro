"""
ExoHunter Pro - A strategic target hunting game module.

This module provides the core gameplay logic for tracking and hunting
targets across different difficulty levels.
"""

import json
import random
from pathlib import Path
from typing import Optional

from issue_tracker import IssueTracker


class ExoHunter:
    """Main game class for ExoHunter Pro."""

    def __init__(self, config_path: Optional[str] = None) -> None:
        """
        Initialize the ExoHunter game instance.

        Args:
            config_path: Path to the configuration file. Defaults to config.json.
        """
        self.config_path = Path(config_path) if config_path else Path("config.json")
        self.config = self._load_config()
        self.score = 0
        self.current_difficulty = "easy"
        self.targets_hunted = 0
        self.active_target: Optional[dict] = None
        self.issue_tracker = IssueTracker()

    def _load_config(self) -> dict:
        """Load configuration from JSON file."""
        if self.config_path.exists():
            with open(self.config_path, "r") as f:
                return json.load(f)
        return {
            "max_targets": 10,
            "difficulty_levels": ["easy", "medium", "hard"],
            "score_thresholds": {"easy": 100, "medium": 250, "hard": 500},
        }

    def hunt(self, target_id: str) -> dict:
        """
        Attempt to hunt a specific target.

        Args:
            target_id: The unique identifier of the target to hunt.

        Returns:
            A dictionary containing the hunt result with status and points.
        """
        if self.targets_hunted >= self.config.get("max_targets", 10):
            return {"status": "failed", "reason": "Maximum targets reached", "points": 0}

        base_points = self._get_base_points()
        difficulty_multiplier = self._get_difficulty_multiplier()
        points_earned = int(base_points * difficulty_multiplier)

        self.score += points_earned
        self.targets_hunted += 1

        return {
            "status": "success",
            "target_id": target_id,
            "points": points_earned,
            "total_score": self.score,
        }

    def track_target(self, sector: str) -> dict:
        """
        Track and locate a target within a specified sector.

        Args:
            sector: The sector identifier to search for targets.

        Returns:
            A dictionary containing target information if found.
        """
        valid_sectors = self.config.get("sectors", ["alpha", "beta", "gamma", "delta"])

        if sector.lower() not in [s.lower() for s in valid_sectors]:
            return {"found": False, "message": f"Invalid sector: {sector}"}

        target_found = random.random() > 0.3
        if target_found:
            target_id = f"TGT-{sector.upper()}-{random.randint(1000, 9999)}"
            self.active_target = {
                "id": target_id,
                "sector": sector,
                "difficulty": self.current_difficulty,
            }
            return {
                "found": True,
                "target": self.active_target,
                "message": f"Target located in sector {sector}",
            }
        return {"found": False, "message": f"No targets detected in sector {sector}"}

    def _get_base_points(self) -> int:
        """Get base points for a successful hunt."""
        return random.randint(50, 150)

    def _get_difficulty_multiplier(self) -> float:
        """Get the difficulty multiplier for score calculation."""
        multipliers = {"easy": 1.0, "medium": 1.5, "hard": 2.5}
        return multipliers.get(self.current_difficulty, 1.0)

    def set_difficulty(self, level: str) -> bool:
        """
        Set the game difficulty level.

        Args:
            level: The difficulty level to set.

        Returns:
            True if the level was set successfully, False otherwise.
        """
        valid_levels = self.config.get("difficulty_levels", ["easy", "medium", "hard"])
        if level.lower() in [l.lower() for l in valid_levels]:
            self.current_difficulty = level.lower()
            return True
        return False

    def get_status(self) -> dict:
        """Get the current game status."""
        return {
            "score": self.score,
            "targets_hunted": self.targets_hunted,
            "max_targets": self.config.get("max_targets", 10),
            "difficulty": self.current_difficulty,
            "active_target": self.active_target,
        }

    def get_repository_files(self) -> list[str]:
        """
        Get list of repository files to verify repository is not empty.

        Returns:
            List of file paths in the repository.

        Fixes:
            GitHub Issue #1: Repository appears empty - now properly detects files.
        """
        repo_files = []
        for ext in ["*.py", "*.json", "*.md", "*.txt", "*.yaml", "*.yml"]:
            repo_files.extend(Path(".").glob(ext))
        return [str(f) for f in repo_files if f.is_file()]

    def verify_repository(self) -> dict:
        """
        Verify the repository has files and is properly configured.

        Returns:
            Dictionary with repository status information.

        Fixes:
            GitHub Issue #1: Repository Empty - AI Code Improvement Request Failed.
        """
        files = self.get_repository_files()
        return {
            "is_empty": len(files) == 0,
            "file_count": len(files),
            "files": files,
            "config_exists": self.config_path.exists(),
            "status": "valid" if files else "empty",
        }

    def log_issue_activity(
        self,
        issue_number: int,
        activity_type: str,
        label: str,
        details: Optional[dict] = None,
    ) -> dict:
        """
        Log activity for a GitHub issue.

        Args:
            issue_number: The issue number.
            activity_type: Type of activity (ai_request, ai_response).
            label: The label associated with the activity.
            details: Optional additional details.

        Returns:
            The log entry dictionary.

        Fixes:
            GitHub Issue #1: AI request/response labeling system.
        """
        if activity_type == "ai_request":
            return self.issue_tracker.log_ai_request(issue_number, label)
        elif activity_type == "ai_response":
            response_len = details.get("response_len", 0) if details else 0
            first_line = details.get("first_line", "") if details else ""
            return self.issue_tracker.log_ai_response(
                issue_number, label, response_len, first_line
            )
        return {"error": "Invalid activity type"}
