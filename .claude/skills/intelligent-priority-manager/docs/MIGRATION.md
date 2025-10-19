# Migration Guide: scan-prioritize-agent to Intelligent Priority Manager

## Overview

This guide helps you migrate from the legacy `scan-prioritize-agent` to the new **Intelligent Priority Manager Skill**. The migration can be done incrementally with minimal disruption to existing workflows.

## Why Migrate?

### Limitations of scan-prioritize-agent
- Simple P0 > P1 > P2 > P3 ordering with no nuance
- No dependency awareness
- No learning from historical patterns
- No consideration of effort or impact
- Basic reporting with minimal insights

### Benefits of Intelligent Priority Manager
- **Multi-factor scoring**: Considers severity, age, dependencies, impact, effort, and frequency
- **Dependency analysis**: Builds dependency graphs and identifies critical paths
- **Pattern learning**: Learns from historical completion patterns
- **Smart recommendations**: Provides actionable insights based on data
- **Parallel work identification**: Suggests items that can be worked simultaneously

## Migration Timeline

### Phase 1: Parallel Running (Week 1-2)
Run both systems side-by-side to compare results and build confidence.

### Phase 2: Primary Switch (Week 3-4)
Make Intelligent Priority Manager the primary system while keeping scan-prioritize-agent as backup.

### Phase 3: Full Cutover (Week 5+)
Remove scan-prioritize-agent completely once confidence is established.

## Pre-Migration Checklist

- [ ] Python 3.8+ installed
- [ ] Poetry or pip available for dependency management
- [ ] Access to feature-management directory
- [ ] Historical data in `completed/` directory (optional but recommended)
- [ ] Backup of existing OVERPROMPT.md workflow

## Step-by-Step Migration

### Step 1: Install Dependencies

```bash
cd .claude/skills/intelligent-priority-manager
poetry install
```

Or using pip:

```bash
pip install -r requirements.txt
```

Verify installation:

```bash
poetry run python3 -c "import networkx; print('Dependencies OK')"
```

### Step 2: Configure Priority Weights

Review and customize `resources/priority_config.json`:

```bash
cd .claude/skills/intelligent-priority-manager
cp resources/priority_config.json resources/priority_config.json.backup
nano resources/priority_config.json
```

**Recommended starting configuration:**

```json
{
  "weights": {
    "severity": 0.30,      // Higher weight for critical bugs
    "age": 0.10,           // Lower initially until backlog cleared
    "dependencies": 0.25,  // Important for unblocking work
    "impact": 0.20,        // Component criticality
    "effort": 0.10,        // Quick wins
    "frequency": 0.05      // Recurring issues
  }
}
```

Adjust weights based on your project's priorities:
- **High urgency project**: Increase `severity` to 0.40-0.50
- **Technical debt focus**: Increase `age` to 0.25-0.30
- **Quick wins focus**: Increase `effort` to 0.20-0.25

### Step 3: Test with Sample Data

Run the skill on your feature-management directory:

```bash
cd .claude/skills/intelligent-priority-manager
./integrate.sh /path/to/feature-management
```

Review the generated report in `feature-management/agent_runs/priority_report_*.md`

### Step 4: Compare Results

Run both systems and compare:

```bash
# Old system (scan-prioritize-agent)
cd /path/to/feature-management
.claude/agents/scan-prioritize-agent/scan.sh > old_priority.txt

# New system (Intelligent Priority Manager)
cd .claude/skills/intelligent-priority-manager
./integrate.sh /path/to/feature-management > new_priority.txt

# Compare
diff old_priority.txt new_priority.txt
```

**Expected differences:**
- Top 3-5 items may shift based on dependencies and impact
- Items blocking others rise in priority
- Old stale items may surface
- Quick wins (low effort) may rank higher

### Step 5: Update OVERPROMPT.md

Modify your workflow to invoke the Skill instead of the agent.

**Before (scan-prioritize-agent):**

```markdown
## Phase 1: Scan and Prioritize

Invoke scan-prioritize-agent to scan bugs/ and features/ directories and generate a priority queue.
```

**After (Intelligent Priority Manager):**

```markdown
## Phase 1: Intelligent Priority Analysis

Invoke the Intelligent Priority Manager Skill to:
1. Scan all bugs/ and features/ directories
2. Analyze dependencies and identify blockers
3. Learn from historical completion patterns
4. Calculate multi-factor priority scores
5. Generate comprehensive priority report with recommendations

The skill will produce a priority report in agent_runs/ with:
- Top priority items with rationale
- Dependency analysis and critical path
- Historical insights and velocity trends
- Recommendations for parallel work opportunities
```

### Step 6: Train on Historical Data

If you have historical data in `completed/` directory:

```bash
# Ensure metadata.json files exist for completed items
cd /path/to/feature-management/completed
ls -d */ | head -5  # Check sample completed items

# Run pattern analysis
cd .claude/skills/intelligent-priority-manager
poetry run python3 scripts/pattern_recognition.py /path/to/feature-management/completed
```

**Historical data format:**

Each completed item should have `metadata.json`:

```json
{
  "id": "BUG-042",
  "status": "completed",
  "original_priority": "P1",
  "severity": "high",
  "components": ["api", "database"],
  "created": "2024-09-01",
  "completed_date": "2024-09-15",
  "estimated_hours": 8,
  "actual_hours": 12,
  "story_points": 5,
  "blockers": ["authentication", "rate_limiting"]
}
```

### Step 7: Validate Dependency Detection

Ensure dependency declarations in PROMPT.md files follow supported patterns:

**Supported dependency patterns:**
```markdown
Depends on: FEAT-003
Blocked by: BUG-012
Requires: FEAT-001
[FEAT-002] must be completed first
```

**Test dependency detection:**

```bash
poetry run python3 scripts/analyze_dependencies.py /path/to/feature-management
```

Review output for:
- All dependencies detected correctly
- No false positives
- Circular dependencies identified (if any)

### Step 8: Tune and Iterate

Monitor results over 2-3 sprints and adjust:

1. **Review priority accuracy**
   - Are high-priority items actually urgent?
   - Are blockers surfacing appropriately?
   - Are quick wins being identified?

2. **Adjust weights** in `priority_config.json`:
   ```bash
   nano resources/priority_config.json
   # Modify weights based on observations
   # Test changes: ./integrate.sh /path/to/feature-management
   ```

3. **Compare with team feedback**
   - Ask team: "Do these priorities make sense?"
   - Adjust if priorities don't align with intuition
   - Document weight changes and rationale

## Rollback Plan

If you need to revert to scan-prioritize-agent:

### Quick Rollback (< 5 minutes)

```bash
cd /path/to/feature-management
git checkout OVERPROMPT.md  # Restore original workflow
```

### Complete Rollback

1. Restore original OVERPROMPT.md
2. Continue using scan-prioritize-agent
3. Document issues encountered
4. File bug report in feature-management repository

## Common Migration Issues

### Issue 1: Performance Slower Than Expected

**Symptom:** Analysis takes >10 seconds for <100 items

**Solution:**
```bash
# Check Python version (3.8+ required)
python3 --version

# Ensure dependencies are properly installed
poetry run python3 -c "import networkx; import sys; print(sys.version)"

# Try direct script execution (bypass shell overhead)
poetry run python3 scripts/analyze_dependencies.py /path/to/feature-management
```

### Issue 2: Priorities Don't Match Expectations

**Symptom:** Lower-priority items ranked higher than expected

**Solution:**
1. Review weight configuration:
   ```bash
   cat resources/priority_config.json | grep -A 8 '"weights"'
   ```
2. Check item metadata in PROMPT.md files
3. Verify severity levels are set correctly
4. Adjust weights to favor critical factors

### Issue 3: Dependencies Not Detected

**Symptom:** Dependency graph is empty or incomplete

**Solution:**
1. Verify dependency syntax in PROMPT.md files:
   ```bash
   grep -r "Depends on\|Blocked by\|Requires" /path/to/feature-management/bugs
   ```
2. Use supported patterns (see Step 7)
3. Check for typos in item IDs (e.g., "BUG-001" vs "bug-001")

### Issue 4: No Historical Patterns Found

**Symptom:** Pattern recognition returns empty results

**Solution:**
1. Ensure `completed/` directory exists and contains items
2. Add metadata.json files to completed items (see Step 6)
3. Need at least 10 completed items for meaningful patterns
4. Pattern learning is optional - skill works without it

### Issue 5: Integration Script Fails

**Symptom:** `./integrate.sh` exits with error

**Solution:**
```bash
# Make script executable
chmod +x integrate.sh

# Check Python path
which python3

# Run scripts individually to isolate issue
poetry run python3 scripts/analyze_dependencies.py /path/to/feature-management
poetry run python3 scripts/calculate_priority.py --feature-dir /path/to/feature-management
```

## Validation Checklist

After migration, verify:

- [ ] Skill runs without errors
- [ ] Priority report is generated in agent_runs/
- [ ] Top 5 priorities make sense to team
- [ ] Dependencies are correctly identified
- [ ] Circular dependencies are detected (if any exist)
- [ ] Performance is acceptable (<5s for typical project)
- [ ] Historical patterns are incorporated (if data available)
- [ ] OVERPROMPT.md workflow invokes skill correctly
- [ ] Team is trained on new priority factors
- [ ] Configuration is version controlled

## Training Team

### Key Concepts to Communicate

1. **Multi-factor scoring** - Priorities now consider multiple factors, not just P0/P1/P2
2. **Dependency awareness** - Items blocking others rank higher
3. **Quick wins** - Lower effort items may rank higher for velocity
4. **Historical learning** - System learns from past completions
5. **Transparent rationale** - Reports explain why items are prioritized

### Sample Team Announcement

```
We're upgrading our prioritization system to be more intelligent and data-driven.

Changes:
- Priority is now calculated from multiple factors (severity, dependencies, impact, etc.)
- The system learns from our historical completion patterns
- You'll see detailed rationale for each priority decision
- Blocking items surface automatically

Benefits:
- Better focus on impactful work
- Fewer surprises from hidden dependencies
- Data-driven decision making
- Clearer understanding of "why this now?"

Your input is valuable - let us know if priorities don't make sense!
```

## Post-Migration Monitoring

### Week 1-2
- Run both systems in parallel
- Compare top 10 priorities daily
- Document discrepancies
- Gather team feedback

### Week 3-4
- Use Intelligent Priority Manager as primary
- Keep scan-prioritize-agent as validation
- Track completion velocity
- Monitor for issues

### Week 5+
- Full cutover to Intelligent Priority Manager
- Remove scan-prioritize-agent from workflow
- Continue monitoring and tuning
- Document lessons learned

## Performance Comparison

Expected metrics:

| Metric | scan-prioritize-agent | Intelligent Priority Manager |
|--------|----------------------|------------------------------|
| Execution time (100 items) | ~0.5s | ~2s |
| Accuracy improvement | Baseline | +30-50% |
| Dependency handling | None | Full graph analysis |
| Learning capability | None | Historical patterns |
| Report detail | Basic | Comprehensive |

## Success Criteria

Migration is successful when:

1. ✅ Team agrees priorities are more accurate
2. ✅ Fewer "why is this low priority?" questions
3. ✅ Blockers are identified proactively
4. ✅ Completion velocity improves or stays stable
5. ✅ System runs reliably in OVERPROMPT workflow
6. ✅ Team understands and trusts priority rationale

## Getting Help

If you encounter issues during migration:

1. **Check troubleshooting** in README.md
2. **Review test cases** in tests/ for usage examples
3. **Examine sample output** in tests/fixtures/
4. **File an issue** in feature-management repository
5. **Rollback if needed** and document the blocker

## Appendix: Configuration Examples

### Example 1: High-Urgency Project

```json
{
  "weights": {
    "severity": 0.45,
    "age": 0.05,
    "dependencies": 0.25,
    "impact": 0.15,
    "effort": 0.05,
    "frequency": 0.05
  }
}
```

### Example 2: Technical Debt Focus

```json
{
  "weights": {
    "severity": 0.15,
    "age": 0.35,
    "dependencies": 0.20,
    "impact": 0.15,
    "effort": 0.10,
    "frequency": 0.05
  }
}
```

### Example 3: Quick Wins Focus

```json
{
  "weights": {
    "severity": 0.20,
    "age": 0.10,
    "dependencies": 0.15,
    "impact": 0.15,
    "effort": 0.30,
    "frequency": 0.10
  }
}
```

## Conclusion

The Intelligent Priority Manager represents a significant upgrade in prioritization capability. Take the migration incrementally, validate results with your team, and don't hesitate to tune the configuration to match your project's needs.

The investment in migration will pay off through better focus, fewer surprises, and more efficient work allocation.

Good luck with your migration!
