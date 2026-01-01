# Verification Pattern (Infrastructure)

## Purpose

Verifies that infrastructure changes have been successfully applied and are working correctly by checking cluster health, service availability, image registries, and deployment status. This pattern provides the quality gate between infrastructure execution and commit, ensuring changes are validated before becoming permanent.

## Problem Statement

Without systematic verification:

- **Silent failures**: Broken deployments go unnoticed
- **Delayed discovery**: Problems found hours or days later
- **Root cause confusion**: Hard to trace what caused issues
- **Incomplete rollouts**: Partial deployments not detected
- **Commit pollution**: Broken changes committed to repository

This pattern solves these problems by providing comprehensive verification checks before changes are committed.

## Responsibilities

### State Verification
- Read task file to understand what was changed
- Determine appropriate verification checks
- Execute verification commands
- Validate results against expected state

### Health Checking
- Check pod status and readiness
- Verify service endpoints
- Test health check endpoints
- Monitor for error events

### Build Verification
- Verify images exist in registry
- Check image tags are correct
- Validate registry accessibility

### Failure Analysis
- Identify root causes of failures
- Determine if issue is task-specific or external
- Provide remediation recommendations

## Workflow

### 1. Read Task Context

Understand what was executed:
- Parse task file labels (determine task type)
- Read acceptance criteria
- Review execution report

### 2. Determine Verification Type

Based on task type:

| Task Type | Verification Focus |
|-----------|-------------------|
| Build | Images in registry |
| Deployment | Pods, services, health |
| Configuration | Resource state, validation |
| Multiple | All applicable checks |

### 3. Execute Safety Checks

Before verification:
- Verify cluster context is correct
- Check Flux is running
- Confirm registry is accessible

If safety checks fail, report BLOCKED.

### 4. Execute Verification Checks

**For Build Tasks:**
- Query registry for image existence
- Verify specific tag is present
- Check registry catalog

**For Deployment Tasks:**
- Check HelmRelease status
- Verify pod status (Running, Ready)
- Check for error events
- Verify service endpoints
- Test health endpoints

**For Configuration Tasks:**
- Validate kustomize build succeeds
- Run security validation
- Verify resource exists with correct config

### 5. Wait for Convergence

Some verifications need time:
- Pod readiness: wait up to 5 minutes
- Flux reconciliation: wait up to 3 minutes
- Retry transient failures after 30 seconds

### 6. Validate Results

For each check:
- **PASS**: Output matches expected state
- **FAIL**: Error, unexpected state, or missing resource
- **WARN**: Potential issue but not blocking

### 7. Analyze Failures

If any check fails:
1. Identify root cause
2. Determine if issue is in this task or external
3. Recommend remediation

Common failure patterns:
- ImagePullBackOff → registry URL or auth issue
- CrashLoopBackOff → application or config error
- Reconciliation failed → chart or values error

### 8. Generate Report

Create verification report with:
- Overall status (PASS/FAIL)
- Detailed check results with evidence
- Root cause analysis for failures
- Recommended remediation
- Next action (commit or fix)

## Input Contract

### Required Inputs

| Field | Type | Description |
|-------|------|-------------|
| `task_id` | string | Task being verified |
| `task_path` | string | Path to task file |

### Optional Inputs

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `execution_report` | object | null | Summary from executor |
| `timeout_seconds` | number | 300 | Maximum wait time |
| `checks_to_run` | array | ["all"] | Specific checks to execute |

## Output Contract

### Success Output (All Passed)

```
{
  "success": true,
  "overall_status": "passed",
  "task_id": "TASK-001",
  "task_type": "build | deployment | configuration",
  "checks": {
    "total": number,
    "passed": number,
    "failed": 0,
    "warnings": number
  },
  "check_results": [
    {
      "name": "Images in registry",
      "status": "pass",
      "command": "command executed",
      "expected": "expected state",
      "actual": "actual state",
      "evidence": "output from check"
    }
  ],
  "next_action": "Signal executor to commit changes"
}
```

### Failure Output

```
{
  "success": false,
  "overall_status": "failed",
  "task_id": "TASK-001",
  "task_type": "deployment",
  "checks": {
    "total": number,
    "passed": number,
    "failed": number,
    "warnings": number
  },
  "check_results": [
    {
      "name": "Pods Running",
      "status": "fail",
      "command": "kubectl get pods -n namespace",
      "expected": "All pods Running",
      "actual": "Pod in ImagePullBackOff",
      "evidence": "detailed output"
    }
  ],
  "failure_analysis": {
    "root_cause": "Image not found in registry",
    "affected_components": ["backend"],
    "is_task_issue": true,
    "remediation": [
      "Check registry URL in HelmRelease",
      "Verify image tag matches pushed version"
    ]
  },
  "next_action": "Return to executor to fix configuration"
}
```

## Decision Rules

### Check Selection by Task Type

| Task Type | Required Checks |
|-----------|-----------------|
| Build | Images in registry, registry accessible |
| Deployment | HelmRelease status, pods, services, health |
| Configuration | Kustomize valid, security valid, resources correct |

### Result Classification

| Condition | Result |
|-----------|--------|
| Output matches expected | PASS |
| Error or unexpected state | FAIL |
| Potential issue, not blocking | WARN |
| Check timed out | FAIL |

### Root Cause Categories

| Symptom | Likely Cause |
|---------|--------------|
| ImagePullBackOff | Registry URL, auth, or missing image |
| CrashLoopBackOff | Application error, missing config, unavailable dependency |
| Reconciliation failed | Chart syntax, invalid values, resource conflict |
| No endpoints | Selector mismatch, pods not ready |

### Retry Logic
- Transient failure → wait 30s, retry once
- Pod not ready → wait up to 5 minutes
- Flux reconciliation → wait up to 3 minutes
- After max retries → mark as FAIL

### Overall Status
- All checks pass → PASSED
- Any check fails → FAILED
- Only warnings → PASSED with warnings

## Integration Pattern

### Receives From

| Agent | Information |
|-------|-------------|
| Infra Executor | What was changed, needs verification |
| Orchestrator | Verification request |

### Sends To

| Agent | Information |
|-------|-------------|
| Infra Executor | Verification result (pass/fail) |
| Summary Reporter | Verification metrics |
| Orchestrator | Overall status and next action |

### Coordination Protocol

1. Invoked after execution phase
2. Runs all applicable verification checks
3. Reports results
4. If PASSED: executor proceeds to commit
5. If FAILED: orchestrator returns to execution or blocks

## Quality Criteria

### Check Completeness
- [ ] All relevant checks executed
- [ ] No checks skipped without reason
- [ ] Timeout applied appropriately
- [ ] Retries attempted for transient failures

### Evidence Quality
- [ ] Command output captured
- [ ] Expected vs actual clearly shown
- [ ] Error messages included
- [ ] Sufficient detail for diagnosis

### Analysis Quality
- [ ] Root cause identified for failures
- [ ] Remediation is actionable
- [ ] Issue correctly attributed (task vs external)
- [ ] Related checks correlated

### Safety
- [ ] Cluster context verified
- [ ] Only read operations performed
- [ ] No production data modified
- [ ] Timeouts prevent hanging

## Implementation Notes

### Verification Checklist by Type

**Build Tasks:**
- [ ] Image appears in registry catalog
- [ ] Expected tag present
- [ ] Image size reasonable

**Deployment Tasks:**
- [ ] HelmRelease reconciled successfully
- [ ] Pods in Running state
- [ ] All containers Ready (X/X)
- [ ] Service endpoints exist
- [ ] Health checks passing
- [ ] No error events

**Configuration Tasks:**
- [ ] Kustomize build validates
- [ ] Security validation passes
- [ ] Resource exists with correct spec
- [ ] No policy violations

### Common Verification Commands

**Registry Checks:**
```
Query registry catalog
Query specific image tags
Verify image exists
```

**Deployment Checks:**
```
Get HelmRelease status
Get pods in namespace
Describe pod for events
Get service endpoints
Test health endpoint
```

**Configuration Checks:**
```
Build kustomize
Run security validation
Get resource YAML
```

### Timeout Strategy
- Quick checks (registry, resource exists): 30 seconds
- Pod readiness: 5 minutes
- Flux reconciliation: 3 minutes
- Overall verification: 10-15 minutes max

### Extensibility
- Custom check definitions per task type
- Configurable timeout values
- Pluggable health check methods
- Custom failure analyzers
