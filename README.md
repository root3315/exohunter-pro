# ExoHunter Pro

A strategic target hunting game with multiple difficulty levels and sector-based tracking.

## Features

- **Target Hunting**: Hunt targets across different sectors with varying success rates
- **Difficulty Levels**: Choose from easy, medium, or hard difficulty
- **Score System**: Earn points based on difficulty and performance
- **Sector Tracking**: Locate targets in different sectors (alpha, beta, gamma, delta, epsilon)

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

## License

MIT License
