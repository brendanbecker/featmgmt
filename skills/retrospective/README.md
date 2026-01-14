# Retrospective Skill

**Description**: Reviews session outcomes, archives items, and reprioritizes backlog.

## Inputs
- **Session Data**: Logs and current state.
- **Backlog**: Current `bugs/` and `features/`.

## Outputs
- **Archived Items**: Moved to `completed/` or `deprecated/`.
- **Updated Backlog**: New priorities in metadata/summaries.
- **Report**: Markdown report of the session.

## Scripts
- `archive_item.py`: Moves and updates items.

## Usage
1. `python3 scripts/archive_item.py <path> --reason "..." --status completed`
