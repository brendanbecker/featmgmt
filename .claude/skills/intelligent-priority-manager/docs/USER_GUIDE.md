# User Guide: Intelligent Priority Manager

## Introduction

The Intelligent Priority Manager helps you automatically prioritize bugs and features using smart algorithms that consider multiple factors beyond just priority labels. This guide explains how to use it effectively.

## What Does It Do?

Instead of simple P0 > P1 > P2 > P3 ordering, the Intelligent Priority Manager:

- Analyzes severity, age, dependencies, impact, effort, and frequency
- Learns from your team's historical completion patterns
- Identifies which items block other work
- Suggests quick wins vs. long-term projects
- Generates reports explaining why items are prioritized a certain way

## Quick Start

### Using with Claude Code

1. **Open your feature-management directory in Claude Code**

2. **Request prioritization:**
   ```
   "Please analyze and prioritize the work items"
   ```

3. **Claude Code will:**
   - Scan all bugs/ and features/ directories
   - Analyze dependencies
   - Calculate priority scores
   - Generate a report

4. **Review the report** in `agent_runs/priority_report_<timestamp>.md`

### Command Line Usage

If you prefer running it manually:

```bash
cd .claude/skills/intelligent-priority-manager
./integrate.sh /path/to/feature-management
```

The script will output a prioritized list and save a detailed report.

## Understanding the Priority Score

Each work item gets a score from 0-100 based on six factors:

### 1. Severity (25% weight by default)
- **Critical**: 100 points
- **High**: 75 points
- **Medium**: 50 points
- **Low**: 25 points
- **Enhancement**: 10 points

### 2. Age (15% weight)
- **Brand new** (< 1 day): 90 points (urgent!)
- **Recent** (1-7 days): 40 points
- **Old** (7-30 days): 60 points
- **Stale** (> 30 days): 80 points (needs attention!)

### 3. Dependencies (20% weight)
How many other items this blocks:
- **Blocks nothing**: 0 points
- **Blocks 1 item**: 50 points
- **Blocks 2-3 items**: 75 points
- **Blocks 4+ items**: 100 points (critical blocker!)

### 4. Impact (20% weight)
Which components are affected:
- **Critical components** (core, security, data): 100 points
- **Multiple components** (3+): 75 points
- **Standard components**: 50 points
- **Single minor component**: 25 points

### 5. Effort (10% weight)
Estimated hours to complete:
- **Quick win** (≤ 2 hours): 100 points
- **Short task** (2-8 hours): 75 points
- **Medium task** (8-40 hours): 50 points
- **Large project** (> 40 hours): 25 points

### 6. Frequency (10% weight)
How often it occurs:
- **Happens once**: 25 points
- **Occasional** (2-5 times): 50 points
- **Frequent** (6-10 times): 75 points
- **Very frequent** (> 10 times): 100 points

## Reading the Priority Report

### Executive Summary

```markdown
## Executive Summary

- **Total Items**: 47
- **Critical Path Length**: 8 items
- **Ready for Work**: 12 items
- **Blocked Items**: 5 items
```

**What this means:**
- You have 47 total bugs/features
- The longest chain of dependencies is 8 items deep
- 12 items can be started immediately (no blockers)
- 5 items are waiting on dependencies

### Top Priority Items

```markdown
### FEAT-003: Git Operations Expert
- **Score**: 87.5/100
- **Original Priority**: P1
- **Factors**:
  - Severity: 75 (high)
  - Dependencies: 100 (blocks 3 items)
  - Impact: 90 (security, core)
  - Effort: 75 (8 hours)
- **Rationale**: High-impact feature blocking multiple dependent items...
```

**How to interpret:**
- **Score**: Overall priority (higher = more urgent)
- **Original Priority**: What it was labeled as
- **Factors**: Breakdown showing why it scored this way
- **Rationale**: Plain English explanation

### Dependency Analysis

```markdown
### Critical Path
BUG-001 → FEAT-001 → FEAT-002 → FEAT-003
```

**What this means:**
- These items form a chain
- You can't start FEAT-001 until BUG-001 is done
- This is your bottleneck - prioritize these items!

### Historical Insights

```markdown
### Velocity Trend
- Week 41: 8 items completed, 13 story points
- Week 42: 6 items completed, 10 story points
- Week 43: 7 items completed, 12 story points
```

**What this tells you:**
- Your team's completion rate
- Trending up or down
- Helps with sprint planning

## Common Scenarios

### Scenario 1: Sprint Planning

**Goal**: Choose items for the next sprint

**Steps:**
1. Run the Intelligent Priority Manager
2. Look at "Ready for Work" section
3. Choose top 5-10 items based on score
4. Verify they fit your sprint capacity (check effort)
5. Check "Parallel Work Opportunities" to maximize team efficiency

**Example:**
```markdown
## Parallel Work Opportunities

These items can be worked on simultaneously:
- FEAT-001, FEAT-004, BUG-007 (no shared dependencies)
- FEAT-002, FEAT-005 (different components)
```

### Scenario 2: Urgent Bug Triage

**Goal**: Determine if a new bug should interrupt current work

**Steps:**
1. Add the bug to bugs/ directory
2. Run prioritization analysis
3. Check if it scores above currently in-progress items
4. Look at "Dependency Analysis" to see if it blocks anything

**Decision criteria:**
- Score > 80: Interrupt current work
- Score 60-80: Add to current sprint
- Score < 60: Backlog for next sprint

### Scenario 3: Reducing Technical Debt

**Goal**: Identify stale items that need attention

**Steps:**
1. Run prioritization analysis
2. Check "Historical Insights" for success patterns
3. Look for items aged > 30 days
4. Review recommendations for process improvements

**Example recommendation:**
```markdown
## Recommendations

- 'testing' is a frequent blocker - prioritize resolving
- Estimates are typically 30% under - adjust estimates upward
- Velocity is low - consider reducing scope or adding resources
```

### Scenario 4: Finding Quick Wins

**Goal**: Boost team morale with easy completions

**Steps:**
1. Run prioritization
2. Sort by "effort" factor (look for 100-point effort scores)
3. Filter items with ≤ 2 hour estimates
4. Choose quick wins that also have high impact

**Why this works:**
- Quick completions build momentum
- High impact quick wins = best ROI
- Reduces work-in-progress count

## Customizing Prioritization

### Adjusting Weights

If the default prioritization doesn't match your needs, edit:
`.claude/skills/intelligent-priority-manager/resources/priority_config.json`

**Example: High-urgency project**
```json
{
  "weights": {
    "severity": 0.35,      // Increase severity importance
    "age": 0.10,           // Decrease age importance
    "dependencies": 0.25,  // Increase dependency importance
    "impact": 0.20,
    "effort": 0.05,        // Decrease effort importance
    "frequency": 0.05
  }
}
```

**Example: Quick wins focus**
```json
{
  "weights": {
    "severity": 0.15,
    "age": 0.10,
    "dependencies": 0.15,
    "impact": 0.15,
    "effort": 0.35,        // Maximize effort importance (quick wins)
    "frequency": 0.10
  }
}
```

### Component Criticality

Define which components are most critical:

```json
{
  "component_criticality": {
    "core": 100,        // Most critical
    "security": 100,
    "payment": 95,      // Very critical
    "api": 70,
    "ui": 50,
    "docs": 30          // Less critical
  }
}
```

## Best Practices

### 1. Declare Dependencies Clearly

In your PROMPT.md files, use clear dependency syntax:

```markdown
## Dependencies
- Depends on: BUG-001
- Blocked by: FEAT-003
- Requires: TASK-005
```

This helps the analyzer build accurate dependency graphs.

### 2. Update Metadata Regularly

Keep item metadata current:
- Update `status` when items are completed
- Adjust `estimated_hours` based on progress
- Track `occurrences` for recurring issues

### 3. Archive Completed Work

Move completed items to `completed/` directory with metadata:

```json
{
  "id": "FEAT-001",
  "completed_date": "2025-10-15",
  "estimated_hours": 8,
  "actual_hours": 10.5,
  "blockers": ["testing", "dependencies"]
}
```

This enables pattern learning and improves future prioritization.

### 4. Review Reports Regularly

- **Daily**: Check top priority items
- **Weekly**: Review velocity trends
- **Monthly**: Analyze historical patterns and adjust config

### 5. Trust the Algorithm, But Use Judgment

The priority score is a recommendation, not a commandment:
- Consider team expertise
- Account for external deadlines
- Factor in stakeholder needs
- Use your domain knowledge

## Troubleshooting

### "No items found"

**Cause**: Empty or missing bugs/features directories

**Solution**: Ensure your feature-management directory has:
```
feature-management/
├── bugs/
│   └── BUG-001/
│       └── PROMPT.md
├── features/
│   └── FEAT-001/
│       └── PROMPT.md
```

### "Circular dependency detected"

**Cause**: Item A depends on B, B depends on C, C depends on A

**Solution**: Review the dependency chain in the report and break the cycle by removing one dependency link.

### "No historical patterns found"

**Cause**: Empty or missing completed/ directory

**Solution**: Start tracking completed items with metadata.json files. Pattern learning requires at least 10 samples.

### Scores seem off

**Cause**: Default weights may not match your project priorities

**Solution**: Adjust weights in `priority_config.json` to reflect your project's unique needs.

## FAQ

**Q: How often should I run prioritization?**
A: Daily for active projects, weekly for maintenance mode.

**Q: Can I prioritize just bugs, not features?**
A: Yes, run analysis only on the bugs/ directory.

**Q: What if two items have the same score?**
A: The original priority label (P0>P1>P2>P3) is used as a tiebreaker.

**Q: Does it replace my team's judgment?**
A: No, it's a tool to inform decisions, not replace human judgment.

**Q: Can I integrate with Jira/GitHub?**
A: Not yet, but this is planned for future versions.

**Q: How accurate is the pattern learning?**
A: Accuracy improves with more historical data. Need 10+ completed items minimum.

## Getting Help

1. **Documentation**: Check README.md and API.md
2. **Examples**: Review test files in tests/ directory
3. **Configuration**: See priority_config.json for all options
4. **Issues**: Report problems in the feature-management repository

## Next Steps

After mastering basic prioritization:

1. **Experiment with weights** to match your workflow
2. **Track completion metrics** to improve pattern learning
3. **Integrate into your sprint planning** process
4. **Share reports** with stakeholders for transparency
5. **Provide feedback** to improve the skill

---

*Remember: The Intelligent Priority Manager is a tool to help you work smarter. Use it as input to your decision-making process, not as a replacement for critical thinking.*
