# Test Runner Skill

**Description**: specialized testing and validation agent responsible for running project tests against the Kubernetes cluster, managing test databases, validating bug fixes, and analyzing results.

## Inputs
- **Codebase**: The current state of the project.
- **Test Configuration**: `pytest.ini`, `package.json`, etc.
- **DATABASE_URL**: Must point to `triager_test`.

## Outputs
- **Test Reports**: Markdown reports in `agent_runs/`.
- **Bug Reports**: New entries in `feature-management/bugs/`.
- **Feature Requests**: New entries in `feature-management/features/`.
- **Human Actions**: Manual test requests in `feature-management/human-actions/`.

## Scripts
- `setup_test_db.sh`: Prepares the test database (Clean/Truncate).
- `run_tests.sh <component>`: Runs tests for backend, frontend, or discord.
- `verify_db_safety.sh`: Ensures we don't touch production DB.
- `create_bulk_pr.sh`: Helper for bulk issue creation.

## Usage
1. Initialize the agent prompt.
2. The agent will check environment and set up DB using `setup_test_db.sh`.
3. The agent will run tests using `run_tests.sh`.
4. The agent will analyze output and create artifacts.
