# Work Item Creation Skill

**Description**: Standardized creation of bugs and features.

## Inputs
- **JSON Input**: Details of the item to create.

## Outputs
- **Work Item Directory**: Created in `feature-management/bugs/` or `features/`.
- **Updated Summaries**: `bugs.md` or `features.md`.

## Scripts
- `create_item.py`: Main logic for generation.

## Usage
`python3 scripts/create_item.py <path-to-json>`
