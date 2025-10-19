# API Documentation

## Overview

This document describes the public APIs of the Intelligent Priority Manager Skill components.

## Core Modules

### analyze_dependencies.py

#### DependencyAnalyzer

Main class for analyzing work item dependencies.

##### Constructor

```python
DependencyAnalyzer(feature_dir: Path)
```

**Parameters:**
- `feature_dir` (Path): Path to the feature-management directory containing bugs/ and features/ subdirectories

**Example:**
```python
from pathlib import Path
from analyze_dependencies import DependencyAnalyzer

analyzer = DependencyAnalyzer(Path('./feature-management'))
```

##### Methods

###### scan_dependencies()

```python
def scan_dependencies() -> Dict[str, List[str]]
```

Scans all work items and extracts their dependencies.

**Returns:**
- Dictionary mapping item IDs to lists of dependency IDs

**Example:**
```python
deps = analyzer.scan_dependencies()
# {'FEAT-001': ['BUG-003'], 'FEAT-002': ['FEAT-001', 'BUG-005']}
```

###### find_critical_path()

```python
def find_critical_path() -> List[str]
```

Identifies the longest dependency chain in the project.

**Returns:**
- List of item IDs forming the critical path (ordered)

**Raises:**
- Prints warning if circular dependencies detected

**Example:**
```python
path = analyzer.find_critical_path()
# ['BUG-001', 'FEAT-001', 'FEAT-002', 'FEAT-003']
```

###### get_ready_items()

```python
def get_ready_items(completed: Set[str]) -> List[str]
```

Determines which items have all dependencies satisfied.

**Parameters:**
- `completed` (Set[str]): Set of already completed item IDs

**Returns:**
- List of item IDs ready to work on

**Example:**
```python
ready = analyzer.get_ready_items({'BUG-001', 'BUG-002'})
# ['FEAT-001', 'FEAT-003']
```

###### analyze()

```python
def analyze() -> Dict
```

Performs complete dependency analysis.

**Returns:**
- Dictionary containing:
  - `dependencies`: Dict mapping items to their dependencies
  - `critical_path`: List of items in critical path
  - `has_cycles`: Boolean indicating circular dependencies
  - `depth`: Length of longest path (or -1 if cycles exist)
  - `components`: List of weakly connected components

**Example:**
```python
results = analyzer.analyze()
print(results['critical_path'])
print(f"Has cycles: {results['has_cycles']}")
```

---

### calculate_priority.py

#### PriorityCalculator

Multi-factor scoring engine for work items.

##### Constructor

```python
PriorityCalculator(config_path: Optional[Path] = None)
```

**Parameters:**
- `config_path` (Optional[Path]): Path to custom configuration JSON. Uses defaults if None.

**Example:**
```python
from pathlib import Path
from calculate_priority import PriorityCalculator

calc = PriorityCalculator(Path('./resources/priority_config.json'))
```

##### Methods

###### calculate_item_score()

```python
def calculate_item_score(item: Dict) -> float
```

Calculates priority score for a single work item.

**Parameters:**
- `item` (Dict): Item metadata with fields:
  - `severity` (str): Severity level (critical, high, medium, low, enhancement)
  - `created` (str): ISO format creation date
  - `blocking` (List[str]): List of items this blocks
  - `components` (List[str]): Affected components
  - `estimated_hours` (float): Effort estimate
  - `occurrences` (int): Frequency of occurrence

**Returns:**
- Float priority score (0-100)

**Example:**
```python
item = {
    'severity': 'critical',
    'created': '2025-10-01',
    'blocking': ['FEAT-002', 'FEAT-003'],
    'components': ['core', 'security'],
    'estimated_hours': 4,
    'occurrences': 10
}
score = calc.calculate_item_score(item)
# 87.5
```

###### prioritize_items()

```python
def prioritize_items(items: List[Dict]) -> List[Dict]
```

Calculates scores for all items and sorts by priority.

**Parameters:**
- `items` (List[Dict]): List of item metadata dictionaries

**Returns:**
- Sorted list of items (highest priority first) with added fields:
  - `priority_score`: Overall score
  - `priority_factors`: Breakdown of individual factor scores

**Example:**
```python
items = [
    {'id': 'BUG-001', 'severity': 'critical', ...},
    {'id': 'FEAT-001', 'severity': 'medium', ...}
]
prioritized = calc.prioritize_items(items)
for item in prioritized:
    print(f"{item['id']}: {item['priority_score']}")
```

##### Private Methods

Internal scoring methods (can be used for debugging):

```python
_severity_score(severity: str) -> float
_age_score(created_date: Optional[str]) -> float
_dependency_score(blocking: List[str]) -> float
_impact_score(components: List[str]) -> float
_effort_score(estimated_hours: float) -> float
_frequency_score(occurrences: int) -> float
```

---

### pattern_recognition.py

#### PatternRecognizer

Historical pattern analysis and learning engine.

##### Constructor

```python
PatternRecognizer(completed_dir: Path)
```

**Parameters:**
- `completed_dir` (Path): Path to directory containing completed work items

**Example:**
```python
from pathlib import Path
from pattern_recognition import PatternRecognizer

recognizer = PatternRecognizer(Path('./feature-management/completed'))
```

##### Methods

###### analyze_historical_patterns()

```python
def analyze_historical_patterns() -> Dict
```

Analyzes all completed items for patterns.

**Returns:**
- Dictionary containing:
  - `completion_time_by_component`: Average times per component
  - `success_rate_by_priority`: Success rates by original priority
  - `velocity_trend`: Weekly velocity data
  - `common_blockers`: Most frequent blockers
  - `effort_accuracy`: Estimation accuracy metrics

**Example:**
```python
patterns = recognizer.analyze_historical_patterns()
print(patterns['completion_time_by_component'])
# {'core': {'mean': 12.5, 'median': 10.0, 'stdev': 3.2}}
```

###### get_recommendations()

```python
def get_recommendations(patterns: Dict) -> List[str]
```

Generates actionable recommendations from patterns.

**Parameters:**
- `patterns` (Dict): Output from analyze_historical_patterns()

**Returns:**
- List of recommendation strings

**Example:**
```python
patterns = recognizer.analyze_historical_patterns()
recs = recognizer.get_recommendations(patterns)
for rec in recs:
    print(f"- {rec}")
# - Estimates are typically 30% under - adjust estimates upward
# - 'testing' is a frequent blocker - prioritize resolving
```

##### Private Methods

```python
_load_completed_items() -> List[Dict]
_analyze_completion_times(items: List[Dict]) -> Dict
_analyze_success_rates(items: List[Dict]) -> Dict
_analyze_velocity_trend(items: List[Dict]) -> List[Dict]
_identify_common_blockers(items: List[Dict]) -> List[Dict]
_analyze_effort_accuracy(items: List[Dict]) -> Dict
```

---

### generate_report.py

#### ReportGenerator

Priority report generation with formatting and templating.

##### Constructor

```python
ReportGenerator(feature_dir: Path, config_path: Optional[Path] = None)
```

**Parameters:**
- `feature_dir` (Path): Feature management directory
- `config_path` (Optional[Path]): Configuration file path

**Example:**
```python
from pathlib import Path
from generate_report import ReportGenerator

generator = ReportGenerator(
    Path('./feature-management'),
    Path('./resources/priority_config.json')
)
```

##### Methods

###### generate_report()

```python
def generate_report(output_path: Optional[Path] = None) -> str
```

Generates complete priority report.

**Parameters:**
- `output_path` (Optional[Path]): Where to write report. If None, returns as string.

**Returns:**
- Report content as markdown string

**Example:**
```python
report = generator.generate_report(Path('./priority_report.md'))
# File written and content returned
```

###### generate_executive_summary()

```python
def generate_executive_summary() -> Dict
```

Creates executive summary metrics.

**Returns:**
- Dictionary with summary statistics

###### generate_priority_queue()

```python
def generate_priority_queue(limit: int = 10) -> List[Dict]
```

Gets top priority items.

**Parameters:**
- `limit` (int): Maximum number of items to return

**Returns:**
- List of prioritized items with full metadata

---

## Data Formats

### Item Metadata Structure

Work items should include these fields in their PROMPT.md metadata:

```yaml
id: FEAT-001
title: Feature Title
severity: critical | high | medium | low | enhancement
priority: P0 | P1 | P2 | P3
status: pending | in-progress | completed | blocked
created: YYYY-MM-DD
components: [component1, component2]
estimated_hours: <float>
occurrences: <int>
blocking: [ITEM-ID1, ITEM-ID2]
```

### Dependency Declarations

Dependencies can be declared in PROMPT.md using these patterns:

```markdown
Depends on: BUG-001
Blocked by: FEAT-003
Requires: TASK-005
[BUG-002] must be completed first
```

### Completed Item Metadata

Completed items should have `metadata.json`:

```json
{
  "id": "FEAT-001",
  "original_priority": "P1",
  "status": "completed",
  "created": "2025-09-01",
  "completed_date": "2025-10-15",
  "components": ["core"],
  "estimated_hours": 8,
  "actual_hours": 10.5,
  "completion_time_hours": 10.5,
  "story_points": 5,
  "blockers": ["testing", "dependencies"]
}
```

### Configuration Schema

```json
{
  "version": "1.0.0",
  "weights": {
    "severity": 0.0-1.0,
    "age": 0.0-1.0,
    "dependencies": 0.0-1.0,
    "impact": 0.0-1.0,
    "effort": 0.0-1.0,
    "frequency": 0.0-1.0
  },
  "severity_scores": {
    "<level>": 0-100
  },
  "age_thresholds": {
    "urgent": <days>,
    "old": <days>,
    "stale": <days>
  },
  "component_criticality": {
    "<component>": 0-100
  },
  "learning": {
    "enabled": true|false,
    "min_samples": <int>,
    "confidence_threshold": 0.0-1.0
  }
}
```

## Command-Line Interface

### analyze_dependencies.py

```bash
poetry run python3 scripts/analyze_dependencies.py <feature_dir>
```

**Output**: JSON to stdout with dependency analysis

### calculate_priority.py

```bash
poetry run python3 scripts/calculate_priority.py \
  --config <config.json> \
  --feature-dir <path>
```

**Output**: JSON to stdout with scored items

### pattern_recognition.py

```bash
poetry run python3 scripts/pattern_recognition.py <completed_dir>
```

**Output**: JSON to stdout with patterns and recommendations

### generate_report.py

```bash
poetry run python3 scripts/generate_report.py \
  --template <template.md> \
  --feature-dir <path> \
  --output <report.md>
```

**Output**: Markdown report file

## Integration Points

### With OVERPROMPT.md

The skill integrates with OVERPROMPT.md workflow at Phase 1:

```markdown
## Phase 1: Planning
Invoke: Intelligent Priority Manager Skill
Input: feature-management directory
Output: Priority queue and report
```

### With Claude Code

Claude Code automatically invokes this skill when:
- User requests "prioritize work items"
- Starting a new development session
- Running sprint planning
- Executing retrospective analysis

### With Other Skills

**Workflow Orchestrator**: Receives priority queue as input
**Git Operations Expert**: Uses priority for commit ordering
**Test Intelligence Suite**: Prioritizes test execution

## Error Handling

All modules raise standard Python exceptions:

- `FileNotFoundError`: Missing directories or files
- `json.JSONDecodeError`: Invalid JSON in metadata
- `ValueError`: Invalid configuration values
- `networkx.NetworkXError`: Graph operation errors

Example error handling:

```python
try:
    analyzer = DependencyAnalyzer(Path('./feature-management'))
    results = analyzer.analyze()
except FileNotFoundError as e:
    print(f"Feature directory not found: {e}")
except Exception as e:
    print(f"Analysis failed: {e}")
```

## Performance Considerations

### Memory Usage

- Dependency graphs: O(n) where n = number of items
- Pattern recognition: O(m) where m = number of completed items
- Peak memory: ~10MB for 1000 items

### Time Complexity

- Dependency scan: O(n × f) where f = files per item (typically 1)
- Critical path: O(n + e) where e = number of edges
- Priority calculation: O(n)
- Pattern analysis: O(m)

### Optimization

For large repositories (>1000 items):

```python
# Cache dependency graph
analyzer = DependencyAnalyzer(feature_dir)
deps = analyzer.scan_dependencies()
# Save to file for reuse

# Limit pattern analysis
recognizer = PatternRecognizer(completed_dir)
# Only analyze recent items
recent_items = [item for item in items
                if item['completed_date'] > '2025-01-01']
```

## Versioning

API follows semantic versioning:
- Major: Breaking changes to public APIs
- Minor: New features, backward compatible
- Patch: Bug fixes

Current version: 1.0.0

## Testing

See test files for comprehensive API usage examples:
- `tests/test_analyze_dependencies.py`
- `tests/test_calculate_priority.py`
- `tests/test_pattern_recognition.py`
- `tests/test_generate_report.py`
