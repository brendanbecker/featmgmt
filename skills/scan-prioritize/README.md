# Scan & Prioritize Skill

**Description**: Scans feature-management repository for unresolved bugs/features and builds a priority queue.

## Inputs
- **Feature Management Repo**: specifically `bugs/bugs.md` and `features/features.md`.

## Outputs
- **Priority Report**: Markdown formatted list of items to work on.
- **Next Item**: Recommendation for what to tackle next.

## Scripts
- `scan.py`: Python script to parse the markdown tables and sort the queue.

## Usage
1. Run `./scripts/scan.py`.
2. Review the output report.
