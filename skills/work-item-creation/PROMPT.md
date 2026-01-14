# Skill: Work Item Creation

You are an agent responsible for creating standardized work items (Bugs, Features).

## Capabilities

1.  **Item Creation**:
    -   Use `scripts/create_item.py` to generate files from JSON input.
    -   Handles ID generation, directory creation, and summary updates.

## Workflow

1.  **Prepare**: Create a JSON file with the item details.
2.  **Execute**: Run `python3 scripts/create_item.py input.json`.
3.  **Result**: The script outputs JSON with the new item ID and path.

## Input JSON Format

```json
{
  "item_type": "bug | feature",
  "title": "...",
  "component": "...",
  "priority": "P0-P3",
  "description": "...",
  "metadata": { ... }
}
```
