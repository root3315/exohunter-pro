# ExoHunter Pro

A strategic target hunting game with multiple difficulty levels and sector-based tracking.

## Features

- **Target Hunting**: Hunt targets across different sectors with varying success rates
- **Difficulty Levels**: Choose from easy, medium, or hard difficulty
- **Score System**: Earn points based on difficulty and performance
- **Sector Tracking**: Locate targets in different sectors (alpha, beta, gamma, delta, epsilon)
- **Issue Tracking**: Built-in GitHub issue tracking with AI request/response labeling

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/exohunter-pro.git
cd exohunter-pro
```

## Usage

```python
from exohunter import ExoHunter

# Initialize the game
game = ExoHunter()

# Verify repository is not empty
repo_status = game.verify_repository()
print(f"Repository files: {repo_status['file_count']}")

# Set difficulty level
game.set_difficulty("medium")

# Track a target in a sector
result = game.track_target("alpha")
if result["found"]:
    # Hunt the located target
    hunt_result = game.hunt(result["target"]["id"])
    print(f"Hunted! Points earned: {hunt_result['points']}")

# Check game status
status = game.get_status()
print(f"Score: {status['score']}")

# Log issue activity (for GitHub integration)
game.log_issue_activity(
    issue_number=1,
    activity_type="ai_request",
    label="issue-body"
)
```

## Configuration

Edit `config.json` to customize game settings:

- `max_targets`: Maximum number of targets that can be hunted (default: 10)
- `difficulty_levels`: Available difficulty levels
- `score_thresholds`: Score thresholds for each difficulty
- `sectors`: Available sectors for target tracking

## API Reference

### ExoHunter Class

#### `__init__(config_path: Optional[str] = None)`
Initialize the game with an optional custom config path.

#### `hunt(target_id: str) -> dict`
Attempt to hunt a specific target. Returns hunt result with status and points.

#### `track_target(sector: str) -> dict`
Track and locate a target within a specified sector. Returns target info if found.

#### `set_difficulty(level: str) -> bool`
Set the game difficulty level. Returns True if successful.

#### `get_status() -> dict`
Get the current game status including score and targets hunted.

#### `verify_repository() -> dict`
Verify the repository has files and is properly configured. Returns repository status.

#### `get_repository_files() -> list[str]`
Get list of repository files to verify repository is not empty.

#### `log_issue_activity(issue_number: int, activity_type: str, label: str, details: Optional[dict] = None) -> dict`
Log activity for a GitHub issue. Supports ai_request and ai_response activity types.

### IssueTracker Class

#### `__init__(issues_path: Optional[str] = None)`
Initialize the issue tracker with an optional custom path.

#### `create_issue(title: str, body: str, labels: Optional[list[str]] = None, issue_number: Optional[int] = None) -> dict`
Create a new issue with the specified title, body, and labels.

#### `add_label(issue_number: int, label: str) -> Optional[dict]`
Add a label to an issue.

#### `remove_label(issue_number: int, label: str) -> Optional[dict]`
Remove a label from an issue.

#### `log_ai_request(issue_number: int, label: str, timestamp: Optional[str] = None) -> dict`
Log an AI request for an issue.

#### `log_ai_response(issue_number: int, label: str, response_len: int, first_line: str, timestamp: Optional[str] = None) -> dict`
Log an AI response for an issue.

#### `get_issue(issue_number: int) -> Optional[dict]`
Get an issue by number.

#### `close_issue(issue_number: int) -> Optional[dict]`
Close an issue.

## Fixed Issues

### Issue #1: Repository Empty - AI Code Improvement Request Failed

**Problem**: The AI code improvement system reported the repository as empty (0 files), causing AI request/response labeling to fail.

**Solution**: 
- Added `issue_tracker.py` module for proper issue tracking and AI labeling
- Added `verify_repository()` method to detect and verify repository files
- Added `get_repository_files()` method to list all source files
- Added `log_issue_activity()` method for AI request/response logging

**Files Changed**:
- `exohunter.py` - Added repository verification and issue logging methods
- `issue_tracker.py` - New module for issue tracking with AI label support

## License

MIT License
