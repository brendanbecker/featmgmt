# Updating Guide

This guide explains how to update existing feature-management projects to the latest featmgmt template version.

## When to Update

### Check for Updates

```bash
cd /path/to/featmgmt
git pull origin master
cat VERSION  # Note the latest version

cd /path/to/project/feature-management
cat .featmgmt-version  # Compare with latest
```

### Update Triggers

**You should update when:**
- New featmgmt version released with bug fixes
- New subagent capabilities available
- Security improvements in templates
- Workflow enhancements you want to adopt
- Periodic maintenance (quarterly recommended)

**You can skip updates when:**
- Current version works perfectly for you
- Heavy customizations make updates risky
- In middle of critical work (update later)

## Update Process

### Step 1: Dry Run

**Always run with --dry-run first:**

```bash
cd /path/to/featmgmt
./scripts/update-project.sh --dry-run /path/to/project/feature-management
```

**Review the output:**
- Which files will change
- Preview of differences
- What customizations might be affected

**Example Output:**
```
Checking for updates...
Project: triager
Type: standard
Current version: 1.0.0
Latest version: 1.1.0

⚠ OVERPROMPT.md: Changes detected
  Preview of changes:
  --- Current
  +++ Template
  @@ -265,0 +266,5 @@
  +## Phase 6: Retrospective → INVOKE retrospective-agent
  +[New retrospective phase added]

✓ agent_actions.md: No changes
✓ .gitignore: No changes

Dry run complete. Run without --dry-run to apply updates.
```

### Step 2: Backup (Automatic)

The update script automatically creates backups, but you can make manual backup too:

```bash
cd /path/to/project
cp -r feature-management feature-management-backup-manual
```

### Step 3: Run Update

```bash
cd /path/to/featmgmt
./scripts/update-project.sh /path/to/project/feature-management
```

**What happens:**
1. Backup created at `.featmgmt-backup-YYYYMMDD-HHMMSS/`
2. OVERPROMPT.md updated from template
3. Common files updated (agent_actions.md, .gitignore)
4. Version files updated
5. Changes logged to UPDATE_LOG.md
6. Git commit created

**Example Output:**
```
Creating backup at .featmgmt-backup-20251018-120000...
✓ Backup created

Applying updates...
Updating OVERPROMPT.md...
✓ OVERPROMPT.md updated
✓ agent_actions.md updated
✓ .gitignore updated

Logging changes...
✓ Changes logged to UPDATE_LOG.md

Committing changes...
✓ Successfully updated to featmgmt v1.1.0

Review changes:
  git log -1 -p

Rollback if needed:
  git reset --hard HEAD~1
  Or restore from backup: .featmgmt-backup-*/
```

### Step 4: Review Changes

```bash
cd /path/to/project/feature-management

# View commit
git log -1 -p

# Check UPDATE_LOG.md
cat UPDATE_LOG.md

# Test workflow
# Open OVERPROMPT.md in Claude Code and verify it works
```

### Step 5: Sync Agents (If Needed)

If subagents were updated:

```bash
cd /path/to/featmgmt
./scripts/sync-agents.sh standard /path/to/project
# or
./scripts/sync-agents.sh gitops /path/to/project
```

**Note:** sync-agents.sh only copies files that don't exist, so customized agents are preserved.

### Step 6: Push Changes

```bash
cd /path/to/project/feature-management
git push origin master
```

## Handling Conflicts

### Scenario 1: Customized OVERPROMPT.md

**Problem:** You heavily customized OVERPROMPT.md, and update overwrites your changes.

**Solution: Manual Merge**

```bash
# Compare your version with backup
diff OVERPROMPT.md .featmgmt-backup-*/OVERPROMPT.md > my-changes.diff

# Compare template with backup
diff .featmgmt-backup-*/OVERPROMPT.md \
     /path/to/featmgmt/templates/OVERPROMPT-standard.md > template-changes.diff

# Review both diffs
cat my-changes.diff
cat template-changes.diff

# Manually merge
# Edit OVERPROMPT.md to incorporate both your customizations and template updates
vim OVERPROMPT.md

# Amend commit
git add OVERPROMPT.md
git commit --amend
```

### Scenario 2: Breaking Changes

**Problem:** New version has breaking changes to workflow.

**Check UPDATE_LOG.md in featmgmt repo:**

```bash
cd /path/to/featmgmt
cat docs/CHANGELOG.md  # Read breaking changes section
```

**Migration Steps:**
- Follow migration guide for your version
- Update custom agents to match new interface
- Test thoroughly with test bug

**Example Migration (1.0.0 → 2.0.0):**
```
Breaking Changes in 2.0.0:
- OVERPROMPT.md now requires Phase 6 (Retrospective)
- Subagents must return JSON instead of markdown

Migration:
1. Add Phase 6 to your OVERPROMPT.md
2. Update custom agents to return JSON format
3. Test with dummy bug before production use
```

### Scenario 3: Custom Agents Broken

**Problem:** Update breaks custom agents.

**Solution:**

```bash
# Restore custom agents from backup
cp .featmgmt-backup-*/custom-agent.md .claude/agents/

# Or update custom agent to match new interface
vim .claude/agents/custom-agent.md

# Test agent
# Create test bug and invoke agent
```

## Rollback Procedures

### Option 1: Git Reset (Simplest)

```bash
cd /path/to/project/feature-management
git reset --hard HEAD~1
```

**Warning:** This loses the update commit. Repush required:
```bash
git push origin master --force
```

### Option 2: Restore from Backup

```bash
cd /path/to/project/feature-management

# Find backup directory
ls -la | grep featmgmt-backup

# Restore specific files
cp .featmgmt-backup-20251018-120000/OVERPROMPT.md .

# Or restore everything
rm -rf *
cp -r .featmgmt-backup-20251018-120000/* .

# Commit restoration
git add .
git commit -m "Rollback update: Restore from backup"
```

### Option 3: Selective Revert

```bash
# Revert only OVERPROMPT.md
git checkout HEAD~1 -- OVERPROMPT.md

# Keep other updates
git add OVERPROMPT.md
git commit -m "Revert OVERPROMPT.md changes, keep other updates"
```

## Update Testing

### Test Checklist

After updating, verify:

- [ ] OVERPROMPT.md opens without errors
- [ ] Subagents can be invoked
- [ ] Scan-prioritize-agent builds queue correctly
- [ ] Bug-processor/infra-executor-agent executes PROMPT.md
- [ ] Test-runner/verification-agent works
- [ ] Git-ops-agent commits and pushes
- [ ] Retrospective-agent runs without errors
- [ ] Summary-reporter-agent generates report

### Test Procedure

1. **Create Test Bug:**
   ```bash
   cd bugs
   mkdir BUG-TEST-update-verification
   cd BUG-TEST-update-verification

   cat > PROMPT.md << 'EOF'
   # BUG-TEST: Update Verification

   ## Description
   Test bug to verify update didn't break workflow.

   ## Acceptance Criteria
   - [ ] Echo "Update successful" to console

   ## Implementation
   Run: echo "Update successful"
   EOF
   ```

2. **Update Summary File:**
   ```bash
   # Add BUG-TEST to bugs/bugs.md
   ```

3. **Run Workflow:**
   ```bash
   # Open OVERPROMPT.md in Claude Code
   # Let it process BUG-TEST
   # Verify all phases complete successfully
   ```

4. **Verify Completion:**
   ```bash
   # Check BUG-TEST moved to completed/
   ls completed/ | grep BUG-TEST

   # Check session report generated
   ls agent_runs/ | tail -1
   ```

5. **Clean Up:**
   ```bash
   # Remove test bug
   rm -rf completed/BUG-TEST-update-verification
   # Update bugs.md to remove test bug
   ```

## Best Practices

### 1. Update Regularly

**Recommended Schedule:**
- Check for updates monthly
- Apply updates quarterly
- Critical security updates: Immediately

**Benefit:** Smaller, incremental updates are easier than large version jumps.

### 2. Test in Development First

**Workflow:**
1. Update dev/staging feature-management
2. Run full test suite
3. Verify no regressions
4. Apply to production

### 3. Document Customizations

**Before updating:**
```json
// .featmgmt-config.json
{
  "customizations": {
    "overprompt_phase_3_modified": "Added security scan step",
    "agent_config_custom_tags": ["payment-system", "third-party-api"],
    "custom_agents": ["security-scanner-agent"]
  }
}
```

**Benefit:** Easier to restore customizations after update.

### 4. Review Changelogs

**Before updating:**
```bash
cd /path/to/featmgmt
git log --oneline $(cat /path/to/project/feature-management/.featmgmt-version)..HEAD
```

**Look for:**
- Breaking changes
- New features you want
- Security fixes
- Bug fixes relevant to your project

### 5. Keep Backups

**Automatic backups:**
- Created by update-project.sh
- Stored in `.featmgmt-backup-*/`

**Manual backups:**
```bash
tar -czf feature-management-backup-$(date +%Y%m%d).tar.gz feature-management/
```

**Backup retention:**
- Keep last 3 automatic backups
- Archive manual backups monthly
- Delete backups older than 6 months

## Updating Multiple Projects

### Batch Update Script

If you have many projects using featmgmt:

```bash
#!/bin/bash
# batch-update.sh

PROJECTS=(
  "/home/becker/projects/triager/feature-management"
  "/home/becker/projects/ccbot/feature-management"
  "/home/becker/projects/midwestmtg/feature-management"
)

for project in "${PROJECTS[@]}"; do
  echo "Updating $project..."
  ./scripts/update-project.sh "$project"
  echo ""
done
```

### Staggered Updates

**Strategy:** Don't update all projects simultaneously

**Example Schedule:**
- Week 1: Update project A
- Week 2: Monitor project A, update project B if A is stable
- Week 3: Monitor A & B, update project C if stable
- Week 4: Update remaining projects

**Benefit:** Catch issues early, minimize blast radius.

## Troubleshooting

### Update Script Fails

**Error: "Not a featmgmt-managed project"**

**Solution:**
```bash
# Add version tracking
echo "1.0.0" > .featmgmt-version

# Create config
cat > .featmgmt-config.json << EOF
{
  "project_name": "myproject",
  "project_type": "standard",
  "featmgmt_version": "1.0.0",
  "initialized_at": "$(date -Iseconds)"
}
EOF

# Try again
./scripts/update-project.sh /path/to/project/feature-management
```

### Merge Conflicts

**Error: "Git merge conflicts"**

**Solution:**
```bash
# Resolve conflicts
git status
vim OVERPROMPT.md  # Resolve conflict markers

# Complete update
git add .
git commit
```

### Agents Not Found

**Error: "Subagent not found: scan-prioritize-agent"**

**Solution:**
```bash
# Sync agents
cd /path/to/featmgmt
./scripts/sync-agents.sh standard /path/to/project

# Verify
ls /path/to/project/.claude/agents/
```

### Workflow Broken After Update

**Error: OVERPROMPT.md fails to execute**

**Solution:**
```bash
# Rollback
git reset --hard HEAD~1

# Compare with template
./scripts/compare-with-template.sh /path/to/project/feature-management standard

# Identify what broke
diff OVERPROMPT.md /path/to/featmgmt/templates/OVERPROMPT-standard.md

# Fix or stay on old version
```

## Version Compatibility

### Supported Upgrade Paths

| From | To | Supported | Notes |
|------|----|-----------| ------|
| 1.0.x | 1.1.x | Yes | Minor update, no breaking changes |
| 1.x.x | 2.0.0 | Yes | Major update, see migration guide |
| 0.9.x | 1.0.0 | No | Pre-release, manual migration required |

### Skipping Versions

**Can you skip versions?**

Yes, but review all intermediate changelogs:

```bash
# Upgrading from 1.0.0 to 1.3.0
# Read changelogs for 1.1.0, 1.2.0, and 1.3.0

cd /path/to/featmgmt
git log --oneline 1.0.0..1.3.0
```

### Long-Term Support

**Maintenance Policy:**
- Latest version: Fully supported
- Previous major version: Security fixes only
- Older versions: No support (upgrade recommended)

## Summary

### Update Process Quick Reference

```bash
# 1. Dry run
./scripts/update-project.sh --dry-run /path/to/project/feature-management

# 2. Review changes
# Read output carefully

# 3. Update
./scripts/update-project.sh /path/to/project/feature-management

# 4. Review commit
cd /path/to/project/feature-management
git log -1 -p

# 5. Test
# Open OVERPROMPT.md, run workflow with test bug

# 6. Sync agents (if needed)
cd /path/to/featmgmt
./scripts/sync-agents.sh <type> /path/to/project

# 7. Push
cd /path/to/project/feature-management
git push origin master
```

### Rollback Quick Reference

```bash
# Option 1: Git reset
cd /path/to/project/feature-management
git reset --hard HEAD~1
git push origin master --force

# Option 2: Restore from backup
cp -r .featmgmt-backup-*/* .
git add .
git commit -m "Rollback update"
git push origin master
```

### Getting Help

- Review docs: [ARCHITECTURE.md](./ARCHITECTURE.md), [CUSTOMIZATION.md](./CUSTOMIZATION.md)
- Check UPDATE_LOG.md in your project
- Compare with template: ./scripts/compare-with-template.sh
- Test with minimal bug
- Rollback if needed

Updates should be smooth and safe. When in doubt, dry run first!
