# FEAT-029: Coverage Tracking & Emergent Discovery

**Priority**: P1
**Component**: skills
**Type**: feature
**Estimated Effort**: Medium
**Technical Complexity**: Medium
**Dependencies**: FEAT-025 (Question-Driven Retrieval), FEAT-026 (Paragraph Extraction & Embedding)

## Overview

Track which paragraphs are "covered" by question-driven retrieval, identify uncovered content via similarity threshold and centroid distance, and cluster emergent content into themes. This ensures valuable research findings that don't directly match original questions are still surfaced in synthesis.

## Problem Statement

During question-driven retrieval (FEAT-025), only paragraphs that semantically match the original questions are retrieved. However, research agents may discover valuable insights that:
- Don't directly answer any posed question
- Represent emergent themes not anticipated when questions were formulated
- Contain cross-cutting concerns relevant to multiple questions
- Identify risks, constraints, or opportunities not in the original scope

Without coverage tracking, these insights are lost in synthesis.

## Key Capabilities

1. **Coverage Tracking**: Maintain set of paragraph IDs retrieved by any question
2. **Configurable Similarity Threshold**: Mark paragraphs as "covered" if similarity >= threshold (default 0.5)
3. **Semantic Outlier Detection**: Identify paragraphs distant from question embedding centroid
4. **Emergent Clustering**: Cluster uncovered paragraphs using AgglomerativeClustering
5. **Theme Label Generation**: Auto-generate descriptive labels for emergent clusters
6. **Coverage Statistics**: Report coverage metrics per source agent

## Acceptance Criteria

- [ ] Coverage tracking: set of paragraph IDs retrieved by any question
- [ ] Configurable similarity threshold for "covered" (default 0.5)
- [ ] Semantic outlier detection (distance from question centroid)
- [ ] Cluster emergent paragraphs (AgglomerativeClustering)
- [ ] Auto-generate theme labels for clusters
- [ ] Coverage statistics per agent

## Implementation Tasks

### Section 1: Coverage Tracking Infrastructure

- [ ] Create `CoverageTracker` class to track retrieved paragraph IDs
- [ ] Integration point with question-driven retrieval (FEAT-025)
- [ ] Mark paragraphs as covered when retrieved for any question
- [ ] Support configurable similarity threshold (default 0.5)
- [ ] Track which question(s) each paragraph was retrieved for

### Section 2: Uncovered Content Detection

- [ ] Identify paragraphs not retrieved by any question
- [ ] Calculate question embedding centroid (mean of all question embeddings)
- [ ] Compute distance from centroid for each uncovered paragraph
- [ ] Flag semantic outliers (distance > threshold from centroid)
- [ ] Distinguish between "near miss" and "truly novel" content

### Section 3: Emergent Clustering

- [ ] Apply AgglomerativeClustering to uncovered paragraph embeddings
- [ ] Auto-determine cluster count using silhouette analysis or distance threshold
- [ ] Group related uncovered content into coherent themes
- [ ] Handle edge cases (few uncovered paragraphs, highly diverse content)

### Section 4: Theme Label Generation

- [ ] Extract key terms from each cluster's paragraphs
- [ ] Generate concise, descriptive labels for each emergent theme
- [ ] Use TF-IDF or embedding similarity to identify representative terms
- [ ] Format labels for human readability

### Section 5: Coverage Statistics & Reporting

- [ ] Calculate coverage percentage per source agent
- [ ] Identify agents with high vs low coverage rates
- [ ] Generate coverage report with:
  - Total paragraphs per agent
  - Covered vs uncovered counts
  - Emergent themes discovered
  - Representative quotes from each theme
- [ ] Output format suitable for synthesis phase

### Section 6: Integration & Testing

- [ ] Integrate with inquiry synthesis workflow
- [ ] Unit tests for coverage tracking
- [ ] Unit tests for clustering logic
- [ ] Integration test with sample research outputs
- [ ] Validate theme labels are meaningful

## Technical Design

### Data Structures

```python
@dataclass
class CoverageTracker:
    covered_ids: Set[str]  # Paragraph IDs retrieved by questions
    paragraph_questions: Dict[str, List[str]]  # paragraph_id -> [question_ids]
    similarity_threshold: float = 0.5

@dataclass
class EmergentCluster:
    cluster_id: int
    label: str
    paragraph_ids: List[str]
    centroid: np.ndarray
    representative_quote: str

@dataclass
class CoverageReport:
    total_paragraphs: int
    covered_count: int
    coverage_percentage: float
    per_agent_stats: Dict[str, AgentCoverageStats]
    emergent_clusters: List[EmergentCluster]
```

### Algorithm Flow

1. After question-driven retrieval completes, collect all retrieved paragraph IDs
2. Identify uncovered paragraphs (all paragraphs - covered set)
3. Compute question centroid from question embeddings
4. Calculate distances from centroid for uncovered paragraphs
5. Apply AgglomerativeClustering to uncovered embeddings
6. Generate labels for each cluster
7. Produce coverage report

### Clustering Parameters

- Distance metric: cosine
- Linkage: average (good for text embeddings)
- Distance threshold: 0.5 (or silhouette-based auto-selection)
- Minimum cluster size: 2 paragraphs

## Dependencies

- **FEAT-025**: Question-Driven Retrieval (provides retrieval results to track)
- **FEAT-026**: Paragraph Extraction & Embedding (provides embeddings to cluster)
- **scikit-learn**: AgglomerativeClustering, silhouette_score
- **numpy**: Centroid calculation, distance metrics

## Usage Example

```python
from coverage_tracker import CoverageTracker, discover_emergent_themes

# After question-driven retrieval
tracker = CoverageTracker(similarity_threshold=0.5)

# Mark paragraphs as covered during retrieval
for question, retrieved_paragraphs in retrieval_results.items():
    for para in retrieved_paragraphs:
        tracker.mark_covered(para.id, question.id)

# Discover emergent content
uncovered = tracker.get_uncovered(all_paragraphs)
emergent_themes = discover_emergent_themes(uncovered, min_clusters=2)

# Generate report
report = tracker.generate_report(all_paragraphs, emergent_themes)
```

## Output Format

```markdown
## Coverage Report

**Total Paragraphs**: 156
**Covered**: 112 (71.8%)
**Uncovered**: 44 (28.2%)

### Per-Agent Coverage

| Agent | Total | Covered | Coverage % |
|-------|-------|---------|------------|
| agent-1 | 52 | 41 | 78.8% |
| agent-2 | 48 | 35 | 72.9% |
| agent-3 | 56 | 36 | 64.3% |

### Emergent Themes (4 clusters)

#### Theme 1: Performance Optimization Concerns
*8 paragraphs from agents 1, 3*

Representative quote:
> "Embedding generation at scale may require batching and caching strategies..."

#### Theme 2: Error Handling Edge Cases
*6 paragraphs from agent 2*

Representative quote:
> "When markdown parsing fails due to malformed code blocks..."
```

## Notes

- Coverage threshold of 0.5 is a starting point; may need tuning based on embedding quality
- Emergent themes should be presented to synthesis agent as additional context
- Consider weighting emergent themes by cluster size and semantic novelty
