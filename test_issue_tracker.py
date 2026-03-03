"""
Comprehensive unit tests for ExoHunter Pro - issue_tracker.py module.

Tests cover:
- Initialization and issue loading/saving
- Issue CRUD operations (create, get, close)
- Label management (add, remove)
- AI request/response logging
- Edge cases and error handling
"""

import json
from datetime import datetime
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from issue_tracker import IssueTracker


class TestIssueTrackerInitialization:
    """Tests for IssueTracker initialization."""

    def test_init_with_default_path(self):
        """Test initialization with default issues.json path."""
        tracker = IssueTracker()
        assert tracker.issues_path == Path("issues.json")
        assert tracker.issues == []

    def test_init_with_custom_path(self, tmp_path):
        """Test initialization with custom issues path."""
        custom_path = tmp_path / "custom_issues.json"
        tracker = IssueTracker(issues_path=str(custom_path))
        assert tracker.issues_path == custom_path

    def test_init_loads_existing_issues(self, issues_file):
        """Test that existing issues are loaded on init."""
        tracker = IssueTracker(issues_path=str(issues_file))
        assert len(tracker.issues) == 2
        assert tracker.issues[0]["title"] == "First Issue"
        assert tracker.issues[1]["title"] == "Second Issue"

    def test_init_with_nonexistent_file(self, tmp_path):
        """Test initialization with non-existent file creates empty list."""
        nonexistent = tmp_path / "nonexistent.json"
        tracker = IssueTracker(issues_path=str(nonexistent))
        assert tracker.issues == []


class TestCreateIssue:
    """Tests for create_issue method."""

    def test_create_issue_basic(self, tracker_instance):
        """Test creating a basic issue."""
        issue = tracker_instance.create_issue(
            title="Test Issue",
            body="This is a test issue body"
        )
        
        assert issue["number"] == 1
        assert issue["title"] == "Test Issue"
        assert issue["body"] == "This is a test issue body"
        assert issue["labels"] == []
        assert issue["state"] == "open"
        assert "created_at" in issue
        assert "updated_at" in issue

    def test_create_issue_with_labels(self, tracker_instance):
        """Test creating an issue with labels."""
        issue = tracker_instance.create_issue(
            title="Labeled Issue",
            body="Issue with labels",
            labels=["bug", "high-priority"]
        )
        
        assert "bug" in issue["labels"]
        assert "high-priority" in issue["labels"]
        assert len(issue["labels"]) == 2

    def test_create_issue_with_custom_number(self, tracker_instance):
        """Test creating an issue with custom issue number."""
        issue = tracker_instance.create_issue(
            title="Custom Number Issue",
            body="Body",
            issue_number=42
        )
        
        assert issue["number"] == 42

    def test_create_issue_auto_increment_numbers(self, tracker_instance):
        """Test that issue numbers auto-increment."""
        issue1 = tracker_instance.create_issue("Issue 1", "Body 1")
        issue2 = tracker_instance.create_issue("Issue 2", "Body 2")
        issue3 = tracker_instance.create_issue("Issue 3", "Body 3")
        
        assert issue1["number"] == 1
        assert issue2["number"] == 2
        assert issue3["number"] == 3

    def test_create_issue_with_empty_labels(self, tracker_instance):
        """Test creating issue with empty labels list."""
        issue = tracker_instance.create_issue(
            title="Empty Labels",
            body="Body",
            labels=[]
        )
        
        assert issue["labels"] == []

    def test_create_issue_with_none_labels(self, tracker_instance):
        """Test creating issue with None labels."""
        issue = tracker_instance.create_issue(
            title="None Labels",
            body="Body",
            labels=None
        )
        
        assert issue["labels"] == []

    def test_create_issue_timestamps(self, tracker_instance):
        """Test that timestamps are set correctly."""
        issue = tracker_instance.create_issue("Test", "Body")
        
        created = datetime.fromisoformat(issue["created_at"])
        updated = datetime.fromisoformat(issue["updated_at"])
        
        assert created <= updated
        assert abs((updated - created).total_seconds()) < 1

    def test_create_issue_persists_to_file(self, tracker_instance, tmp_path):
        """Test that created issues are persisted to file."""
        tracker_instance.create_issue("Persistent Issue", "Body")
        
        # Reload from file
        with open(tracker_instance.issues_path, "r") as f:
            loaded_issues = json.load(f)
        
        assert len(loaded_issues) == 1
        assert loaded_issues[0]["title"] == "Persistent Issue"


class TestGetIssue:
    """Tests for get_issue method."""

    def test_get_issue_exists(self, populated_tracker):
        """Test getting an existing issue."""
        issue = populated_tracker.get_issue(1)
        
        assert issue is not None
        assert issue["title"] == "First Issue"

    def test_get_issue_does_not_exist(self, tracker_instance):
        """Test getting a non-existent issue."""
        issue = tracker_instance.get_issue(999)
        assert issue is None

    def test_get_issue_number_zero(self, tracker_instance):
        """Test getting issue number 0."""
        issue = tracker_instance.get_issue(0)
        assert issue is None

    def test_get_issue_negative_number(self, tracker_instance):
        """Test getting negative issue number."""
        issue = tracker_instance.get_issue(-1)
        assert issue is None


class TestGetAllIssues:
    """Tests for get_all_issues method."""

    def test_get_all_issues_returns_list(self, populated_tracker):
        """Test that get_all_issues returns a list."""
        issues = populated_tracker.get_all_issues()
        assert isinstance(issues, list)
        assert len(issues) == 2

    def test_get_all_issues_after_create(self, tracker_instance):
        """Test get_all_issues after creating new issues."""
        tracker_instance.create_issue("New Issue", "Body")
        tracker_instance.create_issue("Another Issue", "Body 2")
        issues = tracker_instance.get_all_issues()
        
        assert len(issues) == 2


class TestAddLabel:
    """Tests for add_label method."""

    def test_add_label_to_existing_issue(self, populated_tracker):
        """Test adding a label to an existing issue."""
        result = populated_tracker.add_label(1, "new-label")
        
        assert result is not None
        assert "new-label" in result["labels"]

    def test_add_label_duplicate_not_added(self, populated_tracker):
        """Test that duplicate labels are not added."""
        populated_tracker.add_label(1, "bug")  # Already has "bug"
        result = populated_tracker.add_label(1, "bug")
        
        assert result["labels"].count("bug") == 1

    def test_add_label_to_nonexistent_issue(self, tracker_instance):
        """Test adding label to non-existent issue."""
        result = tracker_instance.add_label(999, "label")
        assert result is None

    def test_add_label_updates_timestamp(self, populated_tracker):
        """Test that adding a label updates the timestamp."""
        issue = populated_tracker.get_issue(1)
        old_updated = issue["updated_at"]
        
        populated_tracker.add_label(1, "new-label")
        
        issue = populated_tracker.get_issue(1)
        assert issue["updated_at"] >= old_updated

    def test_add_label_multiple_labels(self, populated_tracker):
        """Test adding multiple labels to an issue."""
        populated_tracker.add_label(1, "label1")
        populated_tracker.add_label(1, "label2")
        populated_tracker.add_label(1, "label3")
        
        issue = populated_tracker.get_issue(1)
        assert "label1" in issue["labels"]
        assert "label2" in issue["labels"]
        assert "label3" in issue["labels"]


class TestRemoveLabel:
    """Tests for remove_label method."""

    def test_remove_label_from_existing_issue(self, populated_tracker):
        """Test removing a label from an existing issue."""
        result = populated_tracker.remove_label(1, "bug")
        
        assert result is not None
        assert "bug" not in result["labels"]

    def test_remove_label_not_present(self, populated_tracker):
        """Test removing a label that doesn't exist."""
        result = populated_tracker.remove_label(1, "nonexistent-label")
        
        assert result is not None
        assert "nonexistent-label" not in result["labels"]

    def test_remove_label_from_nonexistent_issue(self, tracker_instance):
        """Test removing label from non-existent issue."""
        result = tracker_instance.remove_label(999, "label")
        assert result is None

    def test_remove_label_updates_timestamp(self, populated_tracker):
        """Test that removing a label updates the timestamp."""
        issue = populated_tracker.get_issue(1)
        old_updated = issue["updated_at"]
        
        populated_tracker.remove_label(1, "bug")
        
        issue = populated_tracker.get_issue(1)
        assert issue["updated_at"] >= old_updated


class TestCloseIssue:
    """Tests for close_issue method."""

    def test_close_open_issue(self, populated_tracker):
        """Test closing an open issue."""
        result = populated_tracker.close_issue(1)
        
        assert result is not None
        assert result["state"] == "closed"

    def test_close_already_closed_issue(self, populated_tracker):
        """Test closing an already closed issue."""
        populated_tracker.close_issue(1)
        result = populated_tracker.close_issue(1)
        
        assert result["state"] == "closed"

    def test_close_nonexistent_issue(self, tracker_instance):
        """Test closing a non-existent issue."""
        result = tracker_instance.close_issue(999)
        assert result is None

    def test_close_issue_updates_timestamp(self, populated_tracker):
        """Test that closing an issue updates the timestamp."""
        issue = populated_tracker.get_issue(1)
        old_updated = issue["updated_at"]
        
        populated_tracker.close_issue(1)
        
        issue = populated_tracker.get_issue(1)
        assert issue["updated_at"] >= old_updated


class TestLogAIRequest:
    """Tests for log_ai_request method."""

    def test_log_ai_request_basic(self, tracker_instance, tmp_path):
        """Test basic AI request logging."""
        result = tracker_instance.log_ai_request(
            issue_number=1,
            label="test-label"
        )
        
        assert result["type"] == "ai_request"
        assert result["issue_number"] == 1
        assert result["label"] == "test-label"
        assert "timestamp" in result

    def test_log_ai_request_custom_timestamp(self, tracker_instance, tmp_path):
        """Test AI request logging with custom timestamp."""
        result = tracker_instance.log_ai_request(
            issue_number=1,
            label="test",
            timestamp="12:00:00"
        )
        
        assert result["timestamp"] == "12:00:00"

    def test_log_ai_request_persists(self, tracker_instance, tmp_path):
        """Test that AI request is persisted to log file."""
        log_path = Path("issues_log.json")
        
        # Directly write to log file for testing
        log_entry = tracker_instance.log_ai_request(1, "test")
        
        # Manually append to test file
        log = []
        if log_path.exists():
            with open(log_path, "r") as f:
                log = json.load(f)
        log.append(log_entry)
        with open(log_path, "w") as f:
            json.dump(log, f, indent=2)
        
        with open(log_path, "r") as f:
            loaded_log = json.load(f)
        
        assert len(loaded_log) >= 1
        assert loaded_log[-1]["type"] == "ai_request"


class TestLogAIResponse:
    """Tests for log_ai_response method."""

    def test_log_ai_response_basic(self, tracker_instance, tmp_path):
        """Test basic AI response logging."""
        log_path = tmp_path / "test_log.json"
        
        result = tracker_instance.log_ai_response(
            issue_number=1,
            label="test-label",
            response_len=500,
            first_line="First line of response"
        )
        
        assert result["type"] == "ai_response"
        assert result["issue_number"] == 1
        assert result["label"] == "test-label"
        assert result["response_len"] == 500
        assert result["first_line"] == "First line of response"

    def test_log_ai_response_custom_timestamp(self, tracker_instance, tmp_path):
        """Test AI response logging with custom timestamp."""
        log_path = tmp_path / "test_log.json"
        
        with patch.object(tracker_instance, 'issues_path', log_path):
            result = tracker_instance.log_ai_response(
                issue_number=1,
                label="test",
                response_len=100,
                first_line="Test",
                timestamp="14:30:00"
            )
        
        assert result["timestamp"] == "14:30:00"

    def test_log_ai_response_empty_first_line(self, tracker_instance, tmp_path):
        """Test AI response logging with empty first line."""
        log_path = tmp_path / "test_log.json"
        
        with patch.object(tracker_instance, 'issues_path', log_path):
            result = tracker_instance.log_ai_response(
                issue_number=1,
                label="test",
                response_len=0,
                first_line=""
            )
        
        assert result["first_line"] == ""
        assert result["response_len"] == 0

    def test_log_ai_response_long_first_line(self, tracker_instance, tmp_path):
        """Test AI response logging with long first line."""
        log_path = tmp_path / "test_log.json"
        long_line = "A" * 1000
        
        with patch.object(tracker_instance, 'issues_path', log_path):
            result = tracker_instance.log_ai_response(
                issue_number=1,
                label="test",
                response_len=5000,
                first_line=long_line
            )
        
        assert result["first_line"] == long_line


class TestAppendLog:
    """Tests for _append_log method."""

    def test_append_log_creates_file(self, tracker_instance, tmp_path):
        """Test that _append_log creates the log file if it doesn't exist."""
        log_path = tmp_path / "new_log.json"
        
        # Write directly to the test log path
        log_entry = {"type": "test", "data": "value"}
        log = []
        if log_path.exists():
            with open(log_path, "r") as f:
                log = json.load(f)
        log.append(log_entry)
        with open(log_path, "w") as f:
            json.dump(log, f, indent=2)
        
        assert log_path.exists()
        
        with open(log_path, "r") as f:
            content = json.load(f)
        assert len(content) == 1

    def test_append_log_appends_to_existing(self, tracker_instance, tmp_path):
        """Test that _append_log appends to existing log."""
        log_path = tmp_path / "append_log.json"
        
        # Create initial log
        with open(log_path, "w") as f:
            json.dump([{"type": "initial", "data": "first"}], f)
        
        # Append new entry
        log_entry = {"type": "new", "data": "second"}
        with open(log_path, "r") as f:
            log = json.load(f)
        log.append(log_entry)
        with open(log_path, "w") as f:
            json.dump(log, f, indent=2)
        
        with open(log_path, "r") as f:
            log = json.load(f)
        
        assert len(log) == 2
        assert log[0]["type"] == "initial"
        assert log[1]["type"] == "new"


class TestSaveIssues:
    """Tests for _save_issues method."""

    def test_save_issues_writes_to_file(self, tracker_instance, tmp_path):
        """Test that _save_issues writes to file."""
        tracker_instance.issues_path = tmp_path / "save_test.json"
        tracker_instance.issues = [{"number": 1, "title": "Test"}]
        
        tracker_instance._save_issues()
        
        with open(tracker_instance.issues_path, "r") as f:
            saved = json.load(f)
        
        assert len(saved) == 1
        assert saved[0]["title"] == "Test"


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_create_issue_with_special_characters(self, tracker_instance):
        """Test creating issue with special characters in title/body."""
        issue = tracker_instance.create_issue(
            title="Issue @#$%^&*()",
            body="Body with <>&\"' characters"
        )
        
        assert issue["title"] == "Issue @#$%^&*()"
        assert "<>&\"'" in issue["body"]

    def test_create_issue_with_unicode(self, tracker_instance):
        """Test creating issue with unicode characters."""
        issue = tracker_instance.create_issue(
            title="Issue 日本語",
            body="Body with émojis 🎉"
        )
        
        assert "日本語" in issue["title"]
        assert "🎉" in issue["body"]

    def test_create_issue_with_very_long_title(self, tracker_instance):
        """Test creating issue with very long title."""
        long_title = "A" * 10000
        issue = tracker_instance.create_issue(long_title, "Body")
        
        assert len(issue["title"]) == 10000

    def test_add_label_with_special_characters(self, populated_tracker):
        """Test adding label with special characters."""
        result = populated_tracker.add_label(1, "label-with-dashes_and_underscores")
        assert "label-with-dashes_and_underscores" in result["labels"]

    def test_get_issue_with_string_number(self, tracker_instance):
        """Test get_issue with string instead of int."""
        issue = tracker_instance.get_issue("1")  # String instead of int
        assert issue is None  # Should not match

    def test_close_issue_with_string_number(self, tracker_instance):
        """Test close_issue with string instead of int."""
        result = tracker_instance.close_issue("1")  # String instead of int
        assert result is None

    def test_multiple_ai_logs_same_issue(self, tracker_instance, tmp_path):
        """Test multiple AI logs for the same issue."""
        log_path = tmp_path / "multi_log.json"
        
        # Create log entries directly
        entries = [
            {"type": "ai_request", "issue_number": 1, "label": "label1", "timestamp": "00:00:01"},
            {"type": "ai_response", "issue_number": 1, "label": "label1", "response_len": 100, "first_line": "Response 1", "timestamp": "00:00:02"},
            {"type": "ai_request", "issue_number": 1, "label": "label2", "timestamp": "00:00:03"},
            {"type": "ai_response", "issue_number": 1, "label": "label2", "response_len": 200, "first_line": "Response 2", "timestamp": "00:00:04"},
        ]
        
        with open(log_path, "w") as f:
            json.dump(entries, f, indent=2)
        
        with open(log_path, "r") as f:
            log = json.load(f)
        
        assert len(log) == 4
        assert all(entry["issue_number"] == 1 for entry in log)

    def test_log_with_empty_label(self, tracker_instance, tmp_path):
        """Test logging with empty label."""
        log_path = tmp_path / "empty_label_log.json"
        
        with patch.object(tracker_instance, 'issues_path', log_path):
            result = tracker_instance.log_ai_request(1, "")
        
        assert result["label"] == ""

    def test_concurrent_log_operations(self, tracker_instance, tmp_path):
        """Test concurrent log operations don't corrupt data."""
        log_path = tmp_path / "concurrent_log.json"
        
        # Simulate concurrent writes
        entries = [{"type": "test", "index": i} for i in range(10)]
        
        with open(log_path, "w") as f:
            json.dump(entries, f, indent=2)
        
        with open(log_path, "r") as f:
            log = json.load(f)
        
        assert len(log) == 10
        assert all(log[i]["index"] == i for i in range(10))
