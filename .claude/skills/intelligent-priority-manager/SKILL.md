---
name: Intelligent Priority Manager
description: Advanced bug/feature prioritization using ML patterns, dependency analysis, and historical learning
---

# Intelligent Priority Manager

## When to Use
This skill is automatically invoked when:
- Scanning feature-management directories for work items
- Explicitly requesting work prioritization
- Running retrospective analysis
- Planning sprint work

## Capabilities
- **Dependency Analysis**: Identifies and respects inter-item dependencies
- **Pattern Recognition**: Learns from historical completion patterns
- **Multi-Factor Scoring**: Considers severity, age, impact, effort, and dependencies
- **Dynamic Adjustment**: Re-prioritizes based on project state changes
- **Predictive Estimation**: Estimates completion likelihood and effort

## Workflow

1. **Data Collection**
   - Scan all bugs/ and features/ directories
   - Parse metadata from PROMPT.md files
   - Read historical data from completed/ directory

2. **Dependency Analysis**
   - Build dependency graph from item references
   - Identify blocking chains
   - Calculate critical paths

3. **Pattern Analysis**
   - Analyze completion times by component
   - Identify success/failure patterns
   - Calculate team velocity by item type

4. **Priority Calculation**
   - Apply multi-factor scoring algorithm
   - Weight factors based on project phase
   - Consider resource availability

5. **Queue Generation**
   - Generate prioritized work queue
   - Include rationale for each priority decision
   - Suggest parallel work opportunities

## Configuration
See `resources/priority_config.json` for tunable parameters.
