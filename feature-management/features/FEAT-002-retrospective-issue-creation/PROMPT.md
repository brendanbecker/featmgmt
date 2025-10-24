# FEAT-002: Empower retrospective-agent to Create New Bugs and Features

## Description

Extend the retrospective-agent to automatically create new bugs and features when analyzing session outcomes and identifying patterns that reveal missing work items, technical debt, improvement opportunities, or systemic issues.

## Problem Statement

Currently, retrospective-agent can:
- Reprioritize existing bugs and features
- Deprecate obsolete items
- Merge duplicate items

But it cannot:
- Create new bugs when analysis reveals technical debt or recurring issues
- Create new features when identifying improvement opportunities
- Capture systemic problems discovered during session analysis
- Track process improvements as actionable work items

This means valuable insights from retrospective analysis don't translate into tracked work.

## Proposed Solution

Enhance retrospective-agent with issue creation capabilities:

1. **Pattern Analysis**: Identify recurring issues, technical debt, and opportunities
2. **Issue Proposal**: Generate well-structured bug/feature proposals
3. **Automated Creation**: Create bug/feature directories with complete metadata
4. **Integration**: Add created items to backlog and summary files
5. **Reporting**: Include created issues in retrospective report

## Acceptance Criteria

- [ ] Retrospective-agent can identify patterns warranting new work items:
  - Recurring failure patterns → bugs for root cause
  - Technical debt identified → bugs or features for remediation
  - Process improvements → features for tooling/automation
  - Component health issues → bugs for infrastructure
  - Missing test coverage → features for testing improvements
- [ ] Agent creates well-structured entries in appropriate directories
- [ ] Generated entries include:
  - Proper metadata (bug_report.json or feature_request.json)
  - PROMPT.md with context from retrospective analysis
  - Rationale explaining why this issue was created
  - Links to session reports that triggered creation
  - Evidence from pattern analysis
- [ ] Agent updates bugs.md / features.md summary files
- [ ] Created issues are included in retrospective report
- [ ] Agent respects duplicate detection (doesn't recreate existing issues)
- [ ] Priority assignment is data-driven and well-justified

## Implementation Plan

### Phase 1: Pattern Detection Logic
**Location**: `claude-agents/shared/retrospective-agent.md`

Add new section: "Pattern-Based Issue Identification"
- Define patterns that warrant bug creation
- Define patterns that warrant feature creation
- Set thresholds for issue creation (avoid noise)

### Phase 2: Issue Proposal Generation
**Location**: `claude-agents/shared/retrospective-agent.md`

Add new section: "Issue Proposal Creation"
- Generate bug/feature metadata from patterns
- Create PROMPT.md content with evidence
- Link back to session reports
- Assign priorities based on impact

### Phase 3: Automated Issue Creation
**Location**: `claude-agents/shared/retrospective-agent.md`

Add new section: "Automated Bug/Feature Creation"
- Create directory structures
- Write metadata files
- Update summary files
- Integrate with existing backlog

### Phase 4: Retrospective Report Integration
**Location**: `claude-agents/shared/retrospective-agent.md`

Update "Generate Retrospective Report" section:
- Include list of created issues
- Show rationale for each
- Provide evidence from analysis

## Use Cases

### Use Case 1: Recurring Test Failures
**Scenario**: Session analysis shows the same test failing across 3 sessions

**Action**: Create bug
- Title: "Flaky test: test_oauth_refresh fails intermittently"
- Component: "testing/reliability"
- Priority: P2
- Evidence: Links to 3 test run reports
- Rationale: "Test fails in 3 of last 5 sessions, indicating reliability issue"

### Use Case 2: Component Degradation
**Scenario**: Kubernetes component has declining test pass rate (100% → 85% → 75%)

**Action**: Create bug
- Title: "Kubernetes component test reliability declining"
- Component: "kubernetes"
- Priority: P1
- Evidence: Component health metrics over time
- Rationale: "Test pass rate declining over 3 sessions, needs investigation"

### Use Case 3: Technical Debt Pattern
**Scenario**: Multiple bugs in same component reveal architectural issue

**Action**: Create feature
- Title: "Refactor OAuth token management architecture"
- Component: "backend/auth"
- Priority: P1
- Evidence: Links to BUG-011, BUG-012, BUG-015 (all token-related)
- Rationale: "5 OAuth bugs in 2 months suggest architectural problem"

### Use Case 4: Missing Automation
**Scenario**: Human action items created for same manual test repeatedly

**Action**: Create feature
- Title: "Automate Discord bot command testing"
- Component: "testing/automation"
- Priority: P2
- Evidence: Links to ACTION-001, ACTION-003, ACTION-007
- Rationale: "Same manual test required 3 times, should be automated"

### Use Case 5: Process Improvement
**Scenario**: Session analysis shows slow priority queue building

**Action**: Create feature
- Title: "Optimize scan-prioritize-agent performance"
- Component: "agents/standard"
- Priority: P2
- Evidence: Session duration metrics
- Rationale: "Scan phase taking 5+ minutes, can be optimized"

## Technical Design

### New Capabilities for retrospective-agent

```markdown
## Pattern-Based Issue Identification

### Bug Creation Triggers

Create new bug when retrospective detects:

**Recurring Failures**:
- Same test fails in N+ sessions (threshold: 3)
- Same component has repeated failures
- Same error pattern across multiple bugs

**Component Health Degradation**:
- Test pass rate declining over sessions
- Bug count increasing for component
- Resolution time increasing

**Technical Debt Indicators**:
- Multiple bugs with same root cause
- Workarounds accumulating
- Code areas with high bug density

**Infrastructure Issues**:
- Environmental failures recurring
- Deployment issues repeating
- Configuration drift detected

### Feature Creation Triggers

Create new feature when retrospective detects:

**Automation Opportunities**:
- Same manual action repeated N+ times
- Same human action item created repeatedly
- Process bottleneck identified

**Tooling Gaps**:
- Session efficiency could be improved
- Missing development/testing tools
- Reporting could be enhanced

**Architectural Improvements**:
- Pattern of bugs suggesting refactor needed
- Component needing redesign
- Scalability issue emerging

**Process Improvements**:
- Workflow inefficiency detected
- Communication gap identified
- Quality gate missing

### Issue Creation Thresholds

**Do NOT create** if:
- Only 1 occurrence (not a pattern)
- Already exists in backlog (duplicate)
- Insufficient evidence (<2 data points)
- Too vague to be actionable

**Create with P0** if:
- Security pattern detected
- Data loss risk identified
- System-wide impact

**Create with P1** if:
- Multiple sessions affected
- Component health critical
- Blocking other work

**Create with P2** if:
- Improvement opportunity
- Process optimization
- Technical debt

### Issue Proposal Generation

When creating bug/feature:

#### 1. Determine Next ID
```bash
cd /path/to/feature-management
ls -d bugs/BUG-* | sort -V | tail -1
# Increment for next ID
```

#### 2. Generate Title
Format: "[Type]: [Clear description from pattern]"
- "Recurring test failure: test_oauth_refresh"
- "Architectural improvement: Refactor token management"
- "Automation opportunity: Discord command testing"

#### 3. Create bug_report.json / feature_request.json

**Bug Example**:
```json
{
  "bug_id": "BUG-043",
  "title": "Recurring test failure: test_oauth_refresh",
  "component": "backend/auth",
  "severity": "medium",
  "priority": "P2",
  "status": "new",
  "type": "bug",
  "created_date": "2025-10-19",
  "discovered_by": "retrospective-agent",
  "session_analysis": "retrospective-2025-10-19-150000.md",
  "evidence": [
    "agent_runs/test-run-2025-10-15-143022.md",
    "agent_runs/test-run-2025-10-17-091533.md",
    "agent_runs/test-run-2025-10-19-110245.md"
  ],
  "pattern": "recurring_test_failure",
  "occurrences": 3,
  "tags": ["technical-debt", "test-reliability", "auth", "auto-generated"]
}
```

**Feature Example**:
```json
{
  "feature_id": "FEAT-016",
  "title": "Automate Discord bot command testing",
  "component": "testing/automation",
  "priority": "P2",
  "status": "new",
  "type": "enhancement",
  "created_date": "2025-10-19",
  "proposed_by": "retrospective-agent",
  "session_analysis": "retrospective-2025-10-19-150000.md",
  "rationale": "Same manual test required 3 times in 2 weeks",
  "evidence": [
    "human-actions/action-001-discord-loan-command",
    "human-actions/action-003-discord-search-command",
    "human-actions/action-007-discord-help-command"
  ],
  "business_value": "medium",
  "estimated_effort": "medium",
  "tags": ["automation", "testing", "discord", "auto-generated"]
}
```

#### 4. Create PROMPT.md

**Bug Template**:
```markdown
# BUG-XXX: [Title]

## Identified By
**Agent**: retrospective-agent
**Analysis Report**: [link to retrospective report]
**Date**: [YYYY-MM-DD]

## Pattern Detected
**Type**: [recurring_test_failure / component_degradation / technical_debt]
**Occurrences**: [count]
**Time Span**: [first to last occurrence]

## Evidence
1. [Link to session report 1] - [what happened]
2. [Link to session report 2] - [what happened]
3. [Link to session report 3] - [what happened]

## Analysis
[Retrospective agent's analysis of the pattern]

## Impact
[What problems this causes, why it matters]

## Acceptance Criteria
- [ ] Root cause identified
- [ ] Pattern no longer occurs
- [ ] Related tests pass consistently
- [ ] Monitoring added to prevent recurrence

## Related Items
- [Links to related bugs/features/actions]
```

**Feature Template**:
```markdown
# FEAT-XXX: [Title]

## Proposed By
**Agent**: retrospective-agent
**Analysis Report**: [link to retrospective report]
**Date**: [YYYY-MM-DD]

## Opportunity Identified
**Type**: [automation / tooling / process_improvement / architecture]
**Rationale**: [Why this feature is needed]

## Evidence
1. [Link to supporting evidence 1]
2. [Link to supporting evidence 2]
3. [Link to supporting evidence 3]

## Current State
[Description of current manual/inefficient process]

## Proposed Solution
[High-level description of proposed improvement]

## Benefits
- [Benefit 1]
- [Benefit 2]
- [Benefit 3]

## Acceptance Criteria
- [ ] [Specific criterion 1]
- [ ] [Specific criterion 2]
- [ ] [Specific criterion 3]

## Related Items
- [Links to related bugs/features/actions]
```
```

## Integration Points

### Modified Files
- `claude-agents/shared/retrospective-agent.md`

### New Sections to Add
1. "Pattern-Based Issue Identification"
2. "Issue Proposal Generation"
3. "Automated Bug/Feature Creation"

### Updated Sections
- "Core Responsibilities" - add issue creation
- "Backlog Actions Taken" - include created issues
- "Generate Retrospective Report" - add created issues section
- "Tools Available" - ensure Write tool included

## Dependencies

- Requires Write tool access (already present)
- Needs Read access to summary files (already present)
- Should use existing duplicate detection logic
- Leverages .agent-config.json for component detection

## Priority and Component

**Priority**: P1 (High) - Enables proactive backlog management
**Component**: agents/shared
**Estimated Effort**: Medium (3-4 hours implementation)

## Testing This Feature

### Test Scenarios

1. **Create Bug from Recurring Test Failure**
   - Simulate 3 sessions with same test failing
   - Run retrospective-agent
   - Verify bug created with proper evidence links

2. **Create Feature from Automation Opportunity**
   - Create 3 human action items for similar tasks
   - Run retrospective-agent
   - Verify feature created proposing automation

3. **Duplicate Detection**
   - Create bug for known pattern
   - Simulate pattern again
   - Verify no duplicate created, existing bug referenced

4. **Threshold Respect**
   - Simulate single occurrence of pattern
   - Verify no issue created (below threshold)

## Success Metrics

- Retrospective-agent creates actionable work items from patterns
- Created issues have strong evidence and rationale
- No noise (appropriate thresholds)
- Integration with existing workflow seamless
- Backlog health improves over time

## Future Enhancements

- Machine learning to detect subtle patterns
- Sentiment analysis of comments to identify frustration points
- Automatic assignment based on component ownership
- Integration with external issue trackers
- Trend prediction for proactive issue creation
