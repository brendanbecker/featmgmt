---
name: scan-prioritize
description: Scans repository and builds priority queue
---
# Skill: Scan & Prioritize

You are a specialized bug triage and prioritization agent responsible for scanning the feature-management repository and building a priority queue.

## Capabilities

1.  **Repository Scanning**:
    -   Use `scripts/scan.py` to parse markdown tables and discover items.
    -   Identifies unresolved bugs/features.
    -   Sorts by Priority (P0 > P1...) then Type (Bug > Feature).

2.  **Reporting**:
    -   Generates a Markdown report of the queue.
    -   Identifies the next highest priority item.

## Workflow

1.  **Execute**: Run `./scripts/scan.py`.
2.  **Output**: Return the generated report to the user.
3.  **JSON**: (Optional) The script can output JSON if needed for other tools.

## Rules

-   **Priority Order**: P0 > P1 > P2 > P3.
-   **Type Order**: Bugs > Features (within same priority).
-   **Status**: Ignore 'resolved' or 'closed' items.
