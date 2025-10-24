# FEAT-002 Implementation Plan

## Overview

This feature extends retrospective-agent to proactively create bugs and features based on pattern analysis, enabling autonomous backlog growth and continuous improvement.

## Architecture

### Components Modified

1. **retrospective-agent.md**
   - Location: `claude-agents/shared/retrospective-agent.md`
   - New sections: Pattern-Based Issue Identification, Issue Creation
   - Updated sections: Core Responsibilities, Backlog Actions, Report

### Data Flow

```
Session Analysis
    ↓
Pattern Detection
    ↓
Identify Issue Opportunities
    ↓
Generate Issue Proposals
    ↓
Check for Duplicates
    ↓
Create Issue Entries
    ↓
Update Summary Files
    ↓
Include in Retrospective Report
```

## Implementation Steps

### Step 1: Add Pattern Detection Logic

**Location**: New section "Pattern-Based Issue Identification" in retrospective-agent.md

**Content**:
```markdown
## Pattern-Based Issue Identification

### When to Create New Issues

The retrospective-agent should create new bugs or features when analysis reveals actionable patterns that aren't already tracked in the backlog.

### Bug Creation Patterns

**Recurring Test Failures**:
Trigger: Same test fails in 3+ sessions within 2 weeks
```python
# Pseudocode
test_failures = collect_failures_from_recent_sessions(sessions=5)
for test_name, failures in test_failures.items():
    if len(failures) >= 3:
        create_bug(
            title=f"Recurring test failure: {test_name}",
            component=detect_component_from_test_path(test_name),
            priority="P2",
            evidence=failures
        )
```

**Component Health Degradation**:
Trigger: Test pass rate declining >15% over 3 sessions
```python
for component in components:
    pass_rates = get_pass_rates_last_n_sessions(component, n=3)
    if pass_rates[0] - pass_rates[-1] > 0.15:  # >15% decline
        create_bug(
            title=f"Component health declining: {component}",
            component=component,
            priority="P1",
            evidence=pass_rates
        )
```

**Technical Debt Accumulation**:
Trigger: 3+ bugs in same component with related root causes
```python
for component in components:
    recent_bugs = get_completed_bugs(component, last_n_sessions=3)
    if len(recent_bugs) >= 3 and share_root_cause(recent_bugs):
        create_feature(
            title=f"Refactor {component} to address systemic issues",
            component=component,
            priority="P1",
            evidence=recent_bugs
        )
```

**Flaky Tests**:
Trigger: Same test passes and fails in same session or across sessions
```python
for test_name, results in test_history.items():
    if has_both_pass_and_fail(results, window=3):
        create_bug(
            title=f"Flaky test: {test_name}",
            component="testing/reliability",
            priority="P2",
            evidence=results
        )
```

### Feature Creation Patterns

**Automation Opportunities**:
Trigger: Same human action type created 3+ times
```python
action_types = group_human_actions_by_similarity()
for action_type, actions in action_types.items():
    if len(actions) >= 3:
        create_feature(
            title=f"Automate {action_type} testing",
            component="testing/automation",
            priority="P2",
            evidence=actions
        )
```

**Process Bottlenecks**:
Trigger: Same workflow step takes excessive time in multiple sessions
```python
for phase in workflow_phases:
    durations = get_phase_durations(phase, last_n_sessions=3)
    if avg(durations) > threshold and std(durations) < 0.2:  # Consistently slow
        create_feature(
            title=f"Optimize {phase} phase performance",
            component="agents/workflow",
            priority="P2",
            evidence=durations
        )
```

**Missing Coverage**:
Trigger: Multiple bugs in areas without test coverage
```python
for component in components:
    bugs = get_bugs_by_component(component)
    coverage = get_test_coverage(component)
    if len(bugs) >= 2 and coverage < 0.5:  # <50% coverage
        create_feature(
            title=f"Add test coverage for {component}",
            component=component,
            priority="P1",
            evidence={"bugs": bugs, "coverage": coverage}
        )
```

**Infrastructure Improvements**:
Trigger: Repeated environmental or deployment issues
```python
env_issues = get_environmental_failures(last_n_sessions=5)
if len(env_issues) >= 3:
    create_feature(
        title="Improve development environment reliability",
        component="infrastructure",
        priority="P1",
        evidence=env_issues
    )
```

### Issue Creation Thresholds

**Minimum Evidence Requirements**:
- Bugs: 2+ occurrences or 1 critical issue
- Features: 3+ occurrences or clear high-impact opportunity
- Time window: Within last 5 sessions (prevent stale pattern detection)

**Do NOT Create When**:
- Issue already exists in backlog (duplicate)
- Only 1 occurrence (not a pattern)
- Evidence is weak or circumstantial
- Too vague to be actionable
- Environmental/external factor (not fixable)
```

### Step 2: Add Issue Proposal Generation

**Location**: New section "Issue Proposal Generation" in retrospective-agent.md

**Content**:
```markdown
## Issue Proposal Generation

### Metadata Generation

When creating bug from pattern:

```json
{
  "bug_id": "BUG-XXX",
  "title": "[Auto] [Pattern type]: [Description]",
  "component": "[detected from evidence]",
  "severity": "[based on impact]",
  "priority": "[based on frequency/impact]",
  "status": "new",
  "type": "bug",
  "created_date": "YYYY-MM-DD",
  "discovered_by": "retrospective-agent",
  "session_analysis": "retrospective-[timestamp].md",
  "pattern": "[recurring_test_failure | component_degradation | technical_debt | flaky_test]",
  "occurrences": [count],
  "evidence": [
    "link-to-session-report-1",
    "link-to-session-report-2",
    "link-to-session-report-3"
  ],
  "tags": ["auto-generated", "pattern-detected", "[component]", "[type]"]
}
```

When creating feature from opportunity:

```json
{
  "feature_id": "FEAT-XXX",
  "title": "[Auto] [Opportunity type]: [Description]",
  "component": "[target area]",
  "priority": "[based on value]",
  "status": "new",
  "type": "enhancement",
  "created_date": "YYYY-MM-DD",
  "proposed_by": "retrospective-agent",
  "session_analysis": "retrospective-[timestamp].md",
  "opportunity": "[automation | process_improvement | tooling | architecture]",
  "rationale": "[clear explanation of why needed]",
  "evidence": [
    "link-to-supporting-data-1",
    "link-to-supporting-data-2"
  ],
  "business_value": "[high | medium | low]",
  "estimated_effort": "[high | medium | low]",
  "tags": ["auto-generated", "improvement", "[component]"]
}
```

### Title Generation

Format: `[Auto] [Type]: [Clear Description]`

**Examples**:
- `[Auto] Recurring failure: test_oauth_token_refresh`
- `[Auto] Component health: Kubernetes test reliability`
- `[Auto] Technical debt: OAuth token architecture refactor`
- `[Auto] Automation: Discord bot command testing`
- `[Auto] Performance: Optimize scan-prioritize phase`

Prefix `[Auto]` makes it clear these were automatically generated.

### Priority Assignment

**P0 Assignment**:
- Security vulnerability pattern detected
- Data loss risk identified
- Multiple P0 bugs share root cause

**P1 Assignment**:
- Component health critical (test pass <70%)
- Blocks multiple other items
- Recurring failures (5+ occurrences)
- High-value automation opportunity

**P2 Assignment** (Default):
- Process improvement opportunity
- Moderate technical debt
- Test coverage gaps
- Recurring but non-critical issues

**P3 Assignment**:
- Nice-to-have improvements
- Low-frequency patterns
- Documentation needs

### Component Detection

Use evidence to determine component:
- Test failures → extract from test file path
- Human actions → extract from action component field
- Session failures → extract from affected component
- Multiple components → use most frequent or "cross-cutting"
```

### Step 3: Add Duplicate Detection

**Location**: Section "Issue Proposal Generation" in retrospective-agent.md

**Add**:
```markdown
### Duplicate Detection

Before creating new issue:

1. **Read Summary Files**:
```bash
cd /path/to/feature-management
cat bugs/bugs.md
cat features/features.md
```

2. **Check for Existing Issues**:
- Same pattern type already tracked
- Same component + similar title
- Same evidence (e.g., same test name)

3. **Similarity Matching**:
Use .agent-config.json duplicate_similarity_threshold (default 0.75)

```python
def is_duplicate(proposed_title, existing_titles, threshold=0.75):
    for existing in existing_titles:
        similarity = calculate_similarity(proposed_title, existing)
        if similarity >= threshold:
            return True, existing
    return False, None
```

4. **Action on Duplicate Found**:
Instead of creating new issue:
- Add comment to existing issue's comments.md
- Update evidence with new session data
- Note in retrospective report: "Updated BUG-XXX with new evidence"
- Consider priority elevation if pattern worsening
```

### Step 4: Add Issue Creation Process

**Location**: New section "Automated Bug/Feature Creation" in retrospective-agent.md

**Content**:
```markdown
## Automated Bug/Feature Creation

### Creation Workflow

#### 1. Determine Next ID
```bash
cd /path/to/feature-management

# For bugs
latest_bug=$(ls -d bugs/BUG-* 2>/dev/null | sed 's/.*BUG-//' | sed 's/-.*//' | sort -n | tail -1)
next_bug_id=$((latest_bug + 1))

# For features
latest_feat=$(ls -d features/FEAT-* 2>/dev/null | sed 's/.*FEAT-//' | sed 's/-.*//' | sort -n | tail -1)
next_feat_id=$((latest_feat + 1))
```

#### 2. Generate Slug
```python
def generate_slug(title):
    # Remove [Auto] prefix
    title = title.replace("[Auto]", "").strip()
    # Extract description after colon
    if ":" in title:
        title = title.split(":", 1)[1].strip()
    # Convert to slug
    slug = title.lower()
    slug = re.sub(r'[^a-z0-9]+', '-', slug)
    slug = slug.strip('-')
    return slug[:50]  # Max 50 chars
```

#### 3. Create Directory
```bash
mkdir -p bugs/BUG-043-recurring-test-oauth-refresh
# or
mkdir -p features/FEAT-016-automate-discord-testing
```

#### 4. Write Metadata File
Use templates from "Issue Proposal Generation" section above.

#### 5. Write PROMPT.md

**Bug PROMPT.md Template**:
```markdown
# BUG-XXX: [Title without [Auto] prefix]

## Automatically Identified

**Agent**: retrospective-agent
**Analysis Report**: `agent_runs/retrospective-[timestamp].md`
**Date**: [YYYY-MM-DD]
**Pattern Type**: [recurring_test_failure | component_degradation | etc.]

## Pattern Evidence

### Occurrence 1
**Session**: [session-timestamp]
**Report**: `agent_runs/[report-file]`
**Details**: [what happened]

### Occurrence 2
**Session**: [session-timestamp]
**Report**: `agent_runs/[report-file]`
**Details**: [what happened]

### Occurrence 3
**Session**: [session-timestamp]
**Report**: `agent_runs/[report-file]`
**Details**: [what happened]

## Analysis Summary

[Retrospective agent's analysis of the pattern]

**Impact**: [what problems this causes]
**Frequency**: [count] occurrences over [timespan]
**Trend**: [Increasing | Stable | Decreasing]

## Recommended Action

[Suggested approach to resolve this issue]

## Acceptance Criteria

- [ ] Pattern no longer occurs
- [ ] Root cause identified and fixed
- [ ] Related tests pass consistently
- [ ] Monitoring added to prevent recurrence

## Related Items

[Links to related bugs, features, sessions]
```

**Feature PROMPT.md Template**:
```markdown
# FEAT-XXX: [Title without [Auto] prefix]

## Automatically Proposed

**Agent**: retrospective-agent
**Analysis Report**: `agent_runs/retrospective-[timestamp].md`
**Date**: [YYYY-MM-DD]
**Opportunity Type**: [automation | process_improvement | etc.]

## Opportunity Evidence

### Evidence 1
**Session**: [session-timestamp]
**Details**: [supporting evidence]

### Evidence 2
**Session**: [session-timestamp]
**Details**: [supporting evidence]

### Evidence 3
**Session**: [session-timestamp]
**Details**: [supporting evidence]

## Rationale

[Clear explanation of why this feature would be valuable]

## Current State

[Description of current manual/inefficient process or gap]

## Proposed Solution

[High-level approach to address the opportunity]

## Expected Benefits

- [Benefit 1]
- [Benefit 2]
- [Benefit 3]

## Success Metrics

- [Metric 1]
- [Metric 2]

## Acceptance Criteria

- [ ] [Criterion 1]
- [ ] [Criterion 2]
- [ ] [Criterion 3]

## Related Items

[Links to related bugs, features, human actions]
```

#### 6. Update Summary Files

**For Bugs** - Add to bugs/bugs.md:
```markdown
| BUG-043 | [Auto] Recurring failure: test_oauth_refresh | backend/auth | medium | P2 | new | bugs/BUG-043-... |
```

**For Features** - Add to features/features.md:
```markdown
| FEAT-016 | [Auto] Automation: Discord bot testing | testing | P2 | new | features/FEAT-016-... |
```

Update statistics section:
- Total count +1
- By priority +1 for appropriate level
- By status: new +1

#### 7. Git Operations

Include in retrospective commit:
```bash
git add bugs/BUG-043-* features/FEAT-016-* bugs/bugs.md features/features.md
# Included in main retrospective commit
```
```

### Step 5: Update Core Responsibilities

**Location**: Section "Core Responsibilities" in retrospective-agent.md

**Add new subsection**:
```markdown
### Pattern-Based Issue Creation
- Analyze session patterns to identify missing work items
- Create bugs for recurring failures and technical debt
- Create features for automation opportunities and improvements
- Generate complete metadata and PROMPT.md for created issues
- Update summary files with new issues
- Include created issues in retrospective report
```

### Step 6: Update Backlog Actions Section

**Location**: Section "Backlog Actions Taken" in retrospective-agent.md

**Add new subsection**:
```markdown
### Items Created ([count])

#### Bugs Created from Patterns

##### BUG-043: Recurring Test Failure - test_oauth_refresh
- **Pattern**: recurring_test_failure
- **Occurrences**: 3 times over 2 weeks
- **Component**: backend/auth
- **Priority**: P2
- **Evidence**:
  - Session 2025-10-15: Test failed with KeyError
  - Session 2025-10-17: Test failed with KeyError
  - Session 2025-10-19: Test failed with KeyError
- **Location**: `bugs/BUG-043-recurring-test-oauth-refresh/`
- **Rationale**: Test failing consistently suggests reliability issue needing investigation

#### Features Created from Opportunities

##### FEAT-016: Automate Discord Bot Command Testing
- **Opportunity**: automation
- **Occurrences**: 3 manual test actions created
- **Component**: testing/automation
- **Priority**: P2
- **Evidence**:
  - ACTION-001: Manual Discord testing
  - ACTION-003: Manual Discord testing
  - ACTION-007: Manual Discord testing
- **Location**: `features/FEAT-016-automate-discord-testing/`
- **Rationale**: Same manual test repeated 3 times in 2 weeks, clear automation opportunity
```

### Step 7: Update Retrospective Report Template

**Location**: Section "Generate Retrospective Report" in retrospective-agent.md

**Add new section after "Backlog Actions Taken"**:
```markdown
---

## Proactive Issue Creation

### New Bugs from Pattern Detection ([count])

#### BUG-043: Recurring Test Failure - test_oauth_refresh
**Pattern**: Recurring Test Failure
**Occurrences**: 3 sessions
**Priority**: P2
**Component**: backend/auth

**Evidence**:
- 2025-10-15: test_oauth_token_refresh failed with KeyError
- 2025-10-17: test_oauth_token_refresh failed with KeyError
- 2025-10-19: test_oauth_token_refresh failed with KeyError

**Analysis**: Same test failing consistently across multiple sessions indicates a reliability issue rather than a one-off failure. Warrants investigation into root cause.

**Location**: `bugs/BUG-043-recurring-test-oauth-refresh/`

### New Features from Opportunity Analysis ([count])

#### FEAT-016: Automate Discord Bot Command Testing
**Opportunity**: Automation
**Occurrences**: 3 manual actions
**Priority**: P2
**Component**: testing/automation

**Evidence**:
- ACTION-001: Manual Discord /loan command testing
- ACTION-003: Manual Discord /search command testing
- ACTION-007: Manual Discord /help command testing

**Analysis**: Creating the same type of manual action repeatedly suggests an automation gap. Automated Discord command testing would improve efficiency and reliability.

**Location**: `features/FEAT-016-automate-discord-testing/`

---
```

## Component Detection Strategy

### For Bugs from Test Failures
```python
# Extract component from test file path
test_path = "tests/backend/auth/test_oauth.py"
component = extract_component_from_path(test_path, config)
# Result: "backend/auth"
```

### For Features from Human Actions
```python
# Extract component from action metadata
actions = [action1, action2, action3]
components = [a.component for a in actions]
component = most_common(components)
# Result: "discord-bot"
```

### For Cross-Cutting Issues
If pattern affects multiple components:
```python
component = "cross-cutting"
tags = ["backend", "auth", "api"]  # All affected
```

## Priority Assignment Logic

### Evidence-Based Priority

**P0 (Critical)**:
- Security pattern detected (keyword: security, auth, unauthorized)
- Data loss pattern (keyword: corruption, data loss)
- System-wide impact (affects 3+ components)

**P1 (High)**:
- Component health critical (<70% test pass rate)
- High frequency (5+ occurrences in 2 weeks)
- Blocks other work (identified in dependency analysis)
- High-value automation (saves 30+ min per session)

**P2 (Medium)**: (Default)
- Moderate frequency (3-4 occurrences)
- Process improvement with clear benefit
- Technical debt with accumulating cost
- Test coverage gap

**P3 (Low)**:
- Low frequency (2 occurrences)
- Nice-to-have improvement
- Documentation enhancement
- Tooling convenience

## Testing This Implementation

### Test Scenarios

1. **Create Bug from Recurring Test Failure**
   - Simulate 3 test runs with same failure
   - Run retrospective-agent
   - Verify bug created with proper evidence

2. **Create Feature from Manual Actions**
   - Create 3 similar human action items
   - Run retrospective-agent
   - Verify feature created proposing automation

3. **Duplicate Detection**
   - Manually create bug for known pattern
   - Trigger pattern again
   - Verify no duplicate created

4. **Threshold Enforcement**
   - Simulate 2 occurrences (below threshold of 3)
   - Verify no issue created
   - Simulate 3rd occurrence
   - Verify issue now created

5. **Priority Assignment**
   - Simulate security-related pattern
   - Verify P0 assigned
   - Simulate process improvement
   - Verify P2 assigned

### Validation Checklist

- [ ] Created bugs have complete metadata
- [ ] PROMPT.md includes all evidence
- [ ] Component detected correctly
- [ ] Priority justified by evidence
- [ ] Summary files updated
- [ ] No duplicates created
- [ ] Retrospective report includes created issues
- [ ] Git commit includes all changes

## Integration with Existing Workflow

### Phase Flow Update

Current retrospective workflow:
1. Analyze session
2. Reprioritize backlog
3. Deprecate/merge items
4. Generate report

**Add after step 2** (before deprecate/merge):
```
2.5. Pattern Analysis & Issue Creation
   - Scan for recurring patterns
   - Identify opportunities
   - Create bugs/features
   - Update summary files
```

This ensures created issues are included in the same retrospective commit.

## Error Handling

### Pattern Detection Failures
If pattern analysis fails:
- Log warning in retrospective report
- Continue with other retrospective tasks
- Include note: "Pattern analysis incomplete"

### Issue Creation Failures
If directory/file creation fails:
- Log error in retrospective report
- Continue with other issues
- Report which issues couldn't be created

### Duplicate Detection Failures
If similarity check fails:
- Default to creating issue (better than missing it)
- Tag with "needs-duplicate-check"
- Note in retrospective report

## Success Criteria

- Retrospective-agent creates well-justified work items from patterns
- Created issues have strong evidence backing
- No noise (appropriate thresholds prevent spam)
- Integration seamless with existing workflow
- Backlog reflects actual technical debt and opportunities

## Future Enhancements

- Confidence scores for pattern detection
- Machine learning for better pattern recognition
- Trend prediction (predict future issues)
- Cross-project pattern analysis
- Integration with external analytics
