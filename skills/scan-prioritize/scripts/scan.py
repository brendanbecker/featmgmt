#!/usr/bin/env python3
import os
import json
import re
import datetime
import sys

# Paths
BASE_DIR = os.getcwd()
FEATURE_MGMT_DIR = os.path.join(BASE_DIR, "feature-management")
BUGS_FILE = os.path.join(FEATURE_MGMT_DIR, "bugs", "bugs.md")
FEATURES_FILE = os.path.join(FEATURE_MGMT_DIR, "features", "features.md")
ACTIONS_FILE = os.path.join(FEATURE_MGMT_DIR, "human-actions", "actions.md")
HUMAN_ACTIONS_DIR = os.path.join(FEATURE_MGMT_DIR, "human-actions")

def parse_markdown_table(file_path):
    """Parses a markdown table into a list of dictionaries."""
    if not os.path.exists(file_path):
        return []
    
    with open(file_path, 'r') as f:
        content = f.read()

    # Find table lines
    lines = content.splitlines()
    table_data = []
    headers = []
    
    in_table = False
    for line in lines:
        if line.strip().startswith("|") and "---" in line:
            in_table = True
            continue # Skip separator
        
        if line.strip().startswith("|"):
            row = [c.strip() for c in line.strip().strip("|").split("|")]
            if not in_table:
                # Headers
                headers = [h.lower().replace(" ", "_") for h in row]
            else:
                # Data
                if len(row) == len(headers):
                    item = dict(zip(headers, row))
                    table_data.append(item)
    
    return table_data

def get_item_path(item_id, type_dir):
    """Finds the path for an item ID."""
    search_dir = os.path.join(FEATURE_MGMT_DIR, type_dir)
    if not os.path.exists(search_dir):
        return None
    
    for d in os.listdir(search_dir):
        if d.startswith(item_id):
            return os.path.join(type_dir, d)
    return None

def scan_repository():
    bugs = parse_markdown_table(BUGS_FILE)
    features = parse_markdown_table(FEATURES_FILE)
    actions = parse_markdown_table(ACTIONS_FILE)

    queue = []
    
    # Process Bugs
    for bug in bugs:
        status = bug.get('status', '').lower()
        if status not in ['resolved', 'closed']:
            path = get_item_path(bug.get('id', ''), 'bugs')
            if path:
                queue.append({
                    'id': bug.get('id'),
                    'type': 'bug',
                    'title': bug.get('title'),
                    'priority': bug.get('priority', 'P2'),
                    'component': bug.get('component'),
                    'status': status,
                    'path': path
                })

    # Process Features
    for feat in features:
        status = feat.get('status', '').lower()
        if status not in ['implemented', 'closed', 'resolved']:
            path = get_item_path(feat.get('id', ''), 'features')
            if path:
                queue.append({
                    'id': feat.get('id'),
                    'type': 'feature',
                    'title': feat.get('title'),
                    'priority': feat.get('priority', 'P2'),
                    'component': feat.get('component'),
                    'status': status,
                    'path': path
                })

    # Sort Queue
    priority_map = {'P0': 0, 'P1': 1, 'P2': 2, 'P3': 3}
    
    def sort_key(item):
        p_val = priority_map.get(item['priority'], 4)
        t_val = 0 if item['type'] == 'bug' else 1
        return (p_val, t_val, item['id'])

    queue.sort(key=sort_key)
    
    return queue, actions

def generate_report(queue, actions):
    print(f"# Bug Resolution Priority Queue")
    print(f"**Scan Date**: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"**Total Unresolved**: {len(queue)}\n")

    current_p = None
    
    for item in queue:
        p = item['priority']
        if p != current_p:
            print(f"## {p} Priority")
            current_p = p
        
        print(f"- **{item['id']}**: {item['title']} - {item['component']} ({item['status']})")
        print(f"  - Location: {item['path']}")

    if queue:
        top = queue[0]
        print(f"\n## Next Action")
        print(f"**Highest Priority Item**: {top['id']}")
        print(f"**Recommendation**: Process this item first.")
    else:
        print(f"\n## Status")
        print("✅ All items resolved.")

if __name__ == "__main__":
    queue, actions = scan_repository()
    generate_report(queue, actions)
    
    # Save JSON
    output = {
        "priority_queue": queue,
        "human_actions": actions,
        "scan_date": datetime.datetime.now().isoformat()
    }
    # print(json.dumps(output, indent=2)) # Optional: output JSON to stdout or file
