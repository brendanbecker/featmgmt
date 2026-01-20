# FEAT-023 Tasks

## Progress Tracking

- [x] Create feature directory and definition files
- [x] Create PROMPT.md with requirements
- [x] Create PLAN.md with architecture
- [x] Create skill directory structure
- [x] Implement SKILL.md
- [x] Implement collect.py orchestrator
- [x] Implement ccmux_monitor.py
- [x] Implement file_monitor.py
- [x] Implement extract.py
- [x] Implement summarize.py
- [x] Create templates
- [x] Test with sample data (INQ-001-test-inquiry)
- [ ] Update features.md summary

## Detailed Tasks

### Phase 1: Skill Structure
- [x] Create `skills/inquiry-collector/` directory
- [ ] Create SKILL.md with frontmatter
- [ ] Create README.md documentation
- [ ] Create scripts/ directory
- [ ] Create templates/ directory

### Phase 2: Core Scripts
- [ ] `collect.py` - main orchestrator
  - [ ] Parse command-line arguments
  - [ ] Load inquiry configuration
  - [ ] Route to appropriate monitor
  - [ ] Coordinate extraction
  - [ ] Update inquiry status
- [ ] `utils.py` - shared utilities
  - [ ] Inquiry path resolution
  - [ ] JSON read/write helpers
  - [ ] Logging configuration

### Phase 3: Monitoring
- [ ] `ccmux_monitor.py`
  - [ ] Find sessions by inquiry tag
  - [ ] Poll for completion status
  - [ ] Read pane output
  - [ ] Handle timeouts
- [ ] `file_monitor.py`
  - [ ] Watch research/ directory
  - [ ] Detect completion markers
  - [ ] Handle partial files

### Phase 4: Processing
- [ ] `extract.py`
  - [ ] Parse section headers
  - [ ] Extract structured content
  - [ ] Handle multiple formats
  - [ ] Validate completeness
- [ ] `summarize.py`
  - [ ] Analyze all reports
  - [ ] Find common themes
  - [ ] Identify divergence
  - [ ] Generate synthesis prompts

### Phase 5: Templates
- [ ] `agent-report.md.j2`
- [ ] `summary.md.j2`

### Phase 6: Testing & Documentation
- [ ] Create sample inquiry fixture
- [ ] Test ccmux mode
- [ ] Test file mode
- [ ] Test error scenarios
- [ ] Update features.md

## Notes

- Using Python for scripting (consistent with other skills)
- Using Jinja2 for templates (standard choice)
- Minimal dependencies (watchdog optional for file mode)
