---
name: Cross-Project Coordinator
description: Manages dependencies and coordinates work across multiple featmgmt projects
---

# Cross-Project Coordinator

## When to Use
This skill is automatically invoked when:
- Managing multi-project dependencies
- Planning coordinated releases
- Analyzing cross-project impact
- Tracking shared components
- Detecting breaking changes
- Generating portfolio reports

## Capabilities
- **Project Discovery**: Automatically finds and registers projects
- **Dependency Mapping**: Tracks inter-project dependencies
- **Version Management**: Coordinates component versions
- **Breaking Change Detection**: Identifies incompatible changes
- **Release Coordination**: Synchronizes multi-project releases
- **Impact Analysis**: Assesses changes across project boundaries

## Coordination Strategies

### Dependency Management
- Direct dependencies (project A uses project B)
- Transitive dependencies (A → B → C)
- Circular dependency detection
- Version compatibility checking

### Release Coordination
- Dependency-ordered releases
- Synchronized version bumps
- Rollback coordination
- Feature flag management

### Communication
- Cross-project notifications
- Shared status dashboard
- Automated sync meetings
- Change announcements

## Configuration
See `resources/coordinator_config.yaml` for multi-project settings.
