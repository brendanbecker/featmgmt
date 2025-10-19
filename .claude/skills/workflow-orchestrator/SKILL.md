---
name: Stateful Workflow Orchestrator
description: Manages complex multi-phase workflows with state persistence, checkpoints, and recovery
---

# Stateful Workflow Orchestrator

## When to Use
This skill is automatically invoked when:
- Starting an OVERPROMPT.md workflow
- Resuming an interrupted workflow
- Managing parallel phase execution
- Requiring workflow state inspection

## Capabilities
- **State Persistence**: Maintains workflow state across sessions
- **Checkpointing**: Creates restore points at phase boundaries
- **Parallel Execution**: Runs independent phases concurrently
- **Failure Recovery**: Automatic retry with exponential backoff
- **Progress Tracking**: Real-time workflow visualization
- **Transaction Support**: Rollback capabilities for failed phases

## Workflow Management

### State Lifecycle
1. **Initialization**: Create workflow instance with unique ID
2. **Execution**: Track phase progress and outputs
3. **Checkpointing**: Save state at configurable intervals
4. **Recovery**: Restore from last checkpoint on failure
5. **Completion**: Archive workflow state and metrics

### Parallel Execution Strategy
- Analyze phase dependencies
- Identify parallelizable phases
- Allocate resources optimally
- Synchronize at convergence points

### Recovery Mechanisms
- Automatic retry with backoff
- State rollback on critical failures
- Manual intervention points
- Partial workflow re-execution

## Configuration
See `resources/workflow_config.yaml` for tunable parameters.
