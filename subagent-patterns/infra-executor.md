# Infrastructure Executor Pattern

## Purpose

Executes infrastructure tasks by following acceptance criteria in task files, handling builds, deployments, configurations, and cluster operations. This is the GitOps variant of the Bug Processor pattern, specialized for infrastructure management with Kubernetes and container operations.

## Problem Statement

Without structured infrastructure execution:

- **Inconsistent execution**: Tasks executed differently each time
- **Lost progress**: Work state isn't tracked between sessions
- **Incomplete changes**: Acceptance criteria partially addressed
- **Unsafe operations**: Production-impacting changes made without verification
- **Poor traceability**: Infrastructure changes not linked to tasks

This pattern solves these problems by providing disciplined, criteria-driven infrastructure execution with progress tracking and safety checks.

## Responsibilities

### Task Parsing
- Read and understand task file structure
- Identify incomplete acceptance criteria
- Parse commands and instructions
- Understand task type from labels

### Task Execution
- Navigate to appropriate project directories
- Execute commands for each criterion
- Handle builds, deployments, configurations
- Verify changes locally before reporting

### Progress Tracking
- Update task progress log
- Check off completed criteria
- Document any issues encountered
- Maintain audit trail

### Change Management
- Update task file with progress
- Stage changes for version control
- Report all modifications
- Commit after verification passes

## Workflow

### 1. Read Task File

Parse complete task:
- Title, priority, labels
- Acceptance criteria (identify unchecked boxes)
- Commands/instructions
- Dependencies section

### 2. Determine Task Type

Based on labels, identify category:

| Labels | Task Type | Operations |
|--------|-----------|------------|
| builds, registry | Build | Build images, push to registry |
| deployment, flux | Deployment | Update HelmReleases, reconcile |
| infrastructure, networking | Configuration | Update manifests, apply configs |
| verification | Verification | Check health, validate state |

### 3. Navigate to Project

Determine which repository based on task context:
- Infrastructure manifests repository
- Service project repositories
- Task repository (for updates)

### 4. Execute Acceptance Criteria

For each unchecked criterion:

**Build Tasks:**
- Set environment variables
- Execute build scripts
- Push images to registry
- Verify images in registry

**Deployment Tasks:**
- Edit HelmRelease/manifest files
- Update versions and configurations
- Validate with kustomize build
- Trigger reconciliation

**Configuration Tasks:**
- Edit Kubernetes manifests
- Run security validation
- Verify syntax and structure
- Do NOT apply directly (Flux handles this)

### 5. Update Task File

After completing criteria:
- Check off completed items: `[x]`
- Update frontmatter (updated date)
- Add progress log entry with timestamp

Example progress entry:
```
- 2024-01-15 14:30: Built service images v0.1.18, pushed to registry
```

### 6. Handle Errors

If command fails:
1. Retry once
2. If still fails, log error in progress log
3. Mark criterion as incomplete
4. Note blocker in report
5. Continue with remaining criteria if possible

### 7. Generate Report

Create execution report with:
- Task summary
- Completed criteria
- Remaining criteria
- Changes made (files, commands)
- Progress log entry added
- Recommended next steps

### 8. Prepare for Verification

After execution:
- Stage all modified files
- Wait for Verification pattern to validate
- Commit only after verification passes

## Input Contract

### Required Inputs

| Field | Type | Description |
|-------|------|-------------|
| `task_id` | string | Task identifier (e.g., "TASK-001") |
| `task_path` | string | Path to task file |

### Optional Inputs

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `criteria_filter` | array | ["all"] | Specific criteria to execute |
| `dry_run` | boolean | false | Validate without executing |
| `skip_verification` | boolean | false | Don't wait for verification |

## Output Contract

### Success Output

```
{
  "success": true,
  "task_id": "TASK-001",
  "task_title": "Build and deploy service images",
  "task_type": "build | deployment | configuration",
  "criteria": {
    "total": number,
    "completed": number,
    "failed": number,
    "remaining": number
  },
  "completed_criteria": [
    {
      "criterion": "Build all containers with version 0.1.18",
      "command": "command executed",
      "output": "success summary",
      "notes": "optional notes"
    }
  ],
  "remaining_criteria": [
    {
      "criterion": "Update HelmRelease to new version",
      "reason": "Waiting for verification"
    }
  ],
  "changes": {
    "files_modified": ["path/to/file1", "path/to/file2"],
    "commands_executed": ["command1", "command2"]
  },
  "progress_log_entry": "2024-01-15 14:30: Built images v0.1.18",
  "status": "ready_for_verification | partially_complete | blocked",
  "next_steps": "Description of what should happen next"
}
```

### Error Output

```
{
  "success": false,
  "task_id": "TASK-001",
  "error": "Build failed",
  "message": "Docker build failed with exit code 1",
  "details": {
    "criterion": "Build backend container",
    "command": "docker build ...",
    "error_output": "error details"
  },
  "completed_before_failure": ["list of completed criteria"],
  "recovery_suggestions": ["check Docker daemon", "verify Dockerfile"]
}
```

## Decision Rules

### Criterion Completion
- Execute only unchecked criteria `[ ]`
- Skip already checked criteria `[x]`
- Execute in order listed
- Stop at first blocking failure (but try remaining independent criteria)

### Task Type Detection

| Label Contains | Task Type |
|----------------|-----------|
| builds, registry | Build |
| deployment, flux | Deployment |
| infrastructure, networking, security | Configuration |
| verification, health | Verification |

### Error Handling

| Error Type | Action |
|------------|--------|
| Command fails once | Retry once |
| Command fails twice | Log, mark incomplete, continue |
| Missing dependency | Block criterion, note in report |
| Permission denied | Block criterion, suggest remediation |

### Safety Checks
Before any command:
1. Verify correct directory
2. Check git branch (usually main/master)
3. Validate syntax for scripts
4. Verify cluster context for kubectl

### Commit Timing
- Do NOT commit until verification passes
- Stage files but wait for verification
- If verification fails, may need to adjust changes

## Integration Pattern

### Receives From

| Agent | Information |
|-------|-------------|
| Task Scanner | Task to process, priority context |
| Orchestrator | Task dispatch |
| Verification | Retry requests after failed verification |

### Sends To

| Agent | Information |
|-------|-------------|
| Verification | What was changed, needs verification |
| Summary Reporter | Execution outcomes |
| Orchestrator | Completion status |

### Coordination Protocol

1. Receives task from orchestrator
2. Executes acceptance criteria
3. Reports to verification agent
4. If verification passes: commits and reports completion
5. If verification fails: may retry or report blocked

## Quality Criteria

### Execution Quality
- [ ] Only incomplete criteria executed
- [ ] Commands executed in correct directories
- [ ] Errors handled gracefully
- [ ] Changes verified locally before reporting

### Progress Tracking
- [ ] All completed criteria checked off
- [ ] Progress log updated with timestamps
- [ ] Frontmatter updated date set
- [ ] Detailed notes on execution

### Safety
- [ ] Production databases never touched
- [ ] Cluster context verified
- [ ] Security validation run for config changes
- [ ] Direct applies avoided (use GitOps)

### Reporting
- [ ] Complete report generated
- [ ] All changes documented
- [ ] Clear next steps provided
- [ ] Blockers identified

## Implementation Notes

### Common Operations

**Build Tasks:**
```
1. Navigate to project directory
2. Set REGISTRY_URL and VERSION
3. Execute build script with --push
4. Verify image in registry catalog
```

**Deployment Tasks:**
```
1. Navigate to infrastructure repo
2. Edit HelmRelease with new version
3. Run kustomize build to validate
4. Wait for Flux reconciliation (via verification)
```

**Configuration Tasks:**
```
1. Navigate to infrastructure repo
2. Edit manifest files
3. Run kustomize build
4. Run security validation
5. Wait for Flux to apply
```

### Progress Log Format

```markdown
## Progress Log
- 2024-01-15 14:30: Built backend v0.1.18 successfully
- 2024-01-15 14:35: Pushed all images to registry
- 2024-01-15 14:40: Updated HelmRelease with new version
```

### Extensibility
- Support for additional task types via label detection
- Custom command handlers per project
- Configurable retry policies
- Pluggable verification integration
