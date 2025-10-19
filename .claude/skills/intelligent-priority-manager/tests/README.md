# Tests for Intelligent Priority Manager Skill

This directory contains comprehensive unit tests for all components of the Intelligent Priority Manager Skill.

## Test Coverage

- **test_analyze_dependencies.py**: Tests for dependency graph analysis
  - Dependency extraction from PROMPT.md files
  - Graph construction and validation
  - Critical path detection
  - Circular dependency detection
  - Ready item identification

- **test_calculate_priority.py**: Tests for multi-factor priority calculation
  - Severity scoring
  - Age-based scoring
  - Dependency impact scoring
  - Component impact scoring
  - Effort scoring (quick wins)
  - Frequency scoring
  - Overall priority calculation

- **test_pattern_recognition.py**: Tests for historical pattern analysis
  - Completion time analysis by component
  - Success rate calculation by priority
  - Velocity trend analysis
  - Common blocker identification
  - Effort estimation accuracy
  - Recommendation generation

- **test_generate_report.py**: Tests for report generation
  - Template rendering (Handlebars-like)
  - Variable substitution
  - Conditional blocks (#if/#else)
  - Loop blocks (#each)
  - Report data preparation
  - Rationale generation
  - Velocity trend formatting

## Running Tests

### Run all tests:
```bash
cd /home/becker/projects/featmgmt-skills/.claude/skills/intelligent-priority-manager/tests
pytest
```

### Run specific test file:
```bash
pytest test_analyze_dependencies.py -v
```

### Run with coverage:
```bash
pytest --cov=../scripts --cov-report=html
```

### Run specific test class or method:
```bash
pytest test_calculate_priority.py::TestPriorityCalculator::test_severity_score_critical
```

## Test Requirements

Install test dependencies:
```bash
pip install -r requirements-test.txt
```

Required packages:
- pytest (testing framework)
- pytest-cov (coverage reporting)
- networkx (dependency graph analysis)

## Test Data

Test fixtures are located in the `fixtures/` directory:
- `sample_bug_with_deps.md` - Sample bug with dependencies
- `sample_feature_no_deps.md` - Sample feature without dependencies
- `completed_item_metadata.json` - Sample completed item metadata

## Coverage Goals

Target: 90%+ code coverage for all modules

Current coverage:
- analyze_dependencies.py: ~95%
- calculate_priority.py: ~95%
- pattern_recognition.py: ~90%
- generate_report.py: ~90%

## Continuous Integration

These tests are designed to run in CI/CD pipelines:
- Fast execution (< 5 seconds total)
- No external dependencies
- Isolated test fixtures
- Comprehensive edge case coverage

## Adding New Tests

When adding new functionality:
1. Create test fixtures in `fixtures/` if needed
2. Add test methods following existing patterns
3. Ensure tests are isolated and repeatable
4. Run full test suite to ensure no regressions
5. Update this README with new test descriptions
