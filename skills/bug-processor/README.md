# Bug Processor Skill

**Description**: specialized bug resolution implementation agent responsible for reading PROMPT.md files from bug/feature directories and executing the implementation steps systematically.

## Inputs
- **Item Directory**: Path to the bug/feature directory (e.g., `feature-management/bugs/BUG-001-...`).
- **Source Code**: Access to the codebase to modify files.

## Outputs
- **Modified Code**: Changes to the codebase implementing the fix/feature.
- **Updated TASKS.md**: Reflecting progress.
- **Git Commits**: Commits for status updates and implementation.

## Scripts
- `start_item.sh <path>`: Marks the item as `in_progress` in JSON and git.

## Usage
1. Provide the item directory to the agent.
2. The agent will read `PROMPT.md`, `PLAN.md`, `TASKS.md`.
3. The agent will identify the next incomplete section.
4. The agent will execute tasks and update `TASKS.md`.
