"""
Issue Tracker Module for ExoHunter Pro.

This module provides issue tracking and labeling functionality for GitHub issues,
including AI request/response handling.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional


class IssueTracker:
    """Track and manage GitHub issues with AI labeling support."""

    def __init__(self, issues_path: Optional[str] = None) -> None:
        """
        Initialize the IssueTracker.

        Args:
            issues_path: Path to store issue data. Defaults to issues.json.
        """
        self.issues_path = Path(issues_path) if issues_path else Path("issues.json")
        self.issues: list[dict] = []
        self._load_issues()

    def _load_issues(self) -> None:
        """Load existing issues from JSON file."""
        if self.issues_path.exists():
            with open(self.issues_path, "r") as f:
                self.issues = json.load(f)

    def _save_issues(self) -> None:
        """Save issues to JSON file."""
        with open(self.issues_path, "w") as f:
            json.dump(self.issues, f, indent=2)

    def create_issue(
        self,
        title: str,
        body: str,
        labels: Optional[list[str]] = None,
        issue_number: Optional[int] = None,
    ) -> dict:
        """
        Create a new issue.

        Args:
            title: Issue title.
            body: Issue body/description.
            labels: Optional list of labels to apply.
            issue_number: Optional issue number (auto-generated if not provided).

        Returns:
            The created issue dictionary.
        """
        if issue_number is None:
            issue_number = len(self.issues) + 1

        issue = {
            "number": issue_number,
            "title": title,
            "body": body,
            "labels": labels or [],
            "state": "open",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }
        self.issues.append(issue)
        self._save_issues()
        return issue

    def add_label(self, issue_number: int, label: str) -> Optional[dict]:
        """
        Add a label to an issue.

        Args:
            issue_number: The issue number.
            label: The label to add.

        Returns:
            The updated issue or None if not found.
        """
        for issue in self.issues:
            if issue["number"] == issue_number:
                if label not in issue["labels"]:
                    issue["labels"].append(label)
                issue["updated_at"] = datetime.now().isoformat()
                self._save_issues()
                return issue
        return None

    def remove_label(self, issue_number: int, label: str) -> Optional[dict]:
        """
        Remove a label from an issue.

        Args:
            issue_number: The issue number.
            label: The label to remove.

        Returns:
            The updated issue or None if not found.
        """
        for issue in self.issues:
            if issue["number"] == issue_number:
                if label in issue["labels"]:
                    issue["labels"].remove(label)
                issue["updated_at"] = datetime.now().isoformat()
                self._save_issues()
                return issue
        return None

    def log_ai_request(self, issue_number: int, label: str, timestamp: Optional[str] = None) -> dict:
        """
        Log an AI request for an issue.

        Args:
            issue_number: The issue number.
            label: The label associated with the request.
            timestamp: Optional timestamp (auto-generated if not provided).

        Returns:
            The log entry dictionary.
        """
        if timestamp is None:
            timestamp = datetime.now().strftime("%H:%M:%S")

        log_entry = {
            "type": "ai_request",
            "issue_number": issue_number,
            "label": label,
            "timestamp": timestamp,
        }
        self._append_log(log_entry)
        return log_entry

    def log_ai_response(
        self,
        issue_number: int,
        label: str,
        response_len: int,
        first_line: str,
        timestamp: Optional[str] = None,
    ) -> dict:
        """
        Log an AI response for an issue.

        Args:
            issue_number: The issue number.
            label: The label associated with the response.
            response_len: Length of the response.
            first_line: First line of the response.
            timestamp: Optional timestamp (auto-generated if not provided).

        Returns:
            The log entry dictionary.
        """
        if timestamp is None:
            timestamp = datetime.now().strftime("%H:%M:%S")

        log_entry = {
            "type": "ai_response",
            "issue_number": issue_number,
            "label": label,
            "response_len": response_len,
            "first_line": first_line,
            "timestamp": timestamp,
        }
        self._append_log(log_entry)
        return log_entry

    def _append_log(self, log_entry: dict) -> None:
        """Append a log entry to the issues log."""
        log_path = Path("issues_log.json")
        log: list[dict] = []
        if log_path.exists():
            with open(log_path, "r") as f:
                log = json.load(f)
        log.append(log_entry)
        with open(log_path, "w") as f:
            json.dump(log, f, indent=2)

    def get_issue(self, issue_number: int) -> Optional[dict]:
        """
        Get an issue by number.

        Args:
            issue_number: The issue number.

        Returns:
            The issue dictionary or None if not found.
        """
        for issue in self.issues:
            if issue["number"] == issue_number:
                return issue
        return None

    def get_all_issues(self) -> list[dict]:
        """Get all issues."""
        return self.issues

    def close_issue(self, issue_number: int) -> Optional[dict]:
        """
        Close an issue.

        Args:
            issue_number: The issue number.

        Returns:
            The updated issue or None if not found.
        """
        for issue in self.issues:
            if issue["number"] == issue_number:
                issue["state"] = "closed"
                issue["updated_at"] = datetime.now().isoformat()
                self._save_issues()
                return issue
        return None
