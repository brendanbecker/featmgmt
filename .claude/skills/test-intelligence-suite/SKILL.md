---
name: Test Intelligence Suite
description: ML-based test optimization with impact analysis, parallel execution, and flaky test detection
---

# Test Intelligence Suite

## When to Use
This skill is automatically invoked when:
- Running test suites
- Analyzing code changes for testing
- Optimizing test execution time
- Investigating test failures
- Managing flaky tests
- Generating coverage reports

## Capabilities
- **Impact Analysis**: Determines which tests to run based on code changes
- **Parallel Execution**: Distributes tests across workers efficiently
- **Coverage Optimization**: Identifies and fills coverage gaps
- **Flaky Test Detection**: Quarantines unreliable tests
- **Failure Prediction**: Predicts likely test failures
- **Time Estimation**: Accurate test execution time predictions

## Test Selection Strategies

### Risk-Based Selection
- High-risk code paths get more testing
- Security-related changes trigger security tests
- Performance changes trigger benchmark tests

### Dependency-Based Selection
- Tests affected by changed dependencies
- Integration tests for API changes
- UI tests for frontend changes

### Historical Selection
- Tests that previously caught bugs in modified code
- Tests that frequently fail together

## Optimization Techniques
- Test order optimization (fail-fast)
- Resource-aware parallelization
- Incremental testing
- Test result caching

## Configuration
See `resources/test_config.yaml` for test suite settings.
