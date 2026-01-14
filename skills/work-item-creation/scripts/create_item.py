#!/usr/bin/env python3
import os
import json
import argparse
import re
from datetime import datetime

# Paths
BASE_DIR = os.getcwd()
FEATURE_MGMT_DIR = os.path.join(BASE_DIR, "feature-management")
TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")

def get_next_id(prefix, directory):
    """Finds the next available ID in a directory."""
    max_id = 0
    if not os.path.exists(directory):
        return 1
    
    for d in os.listdir(directory):
        match = re.match(f"{prefix}-(\d+)-", d)
        if match:
            num = int(match.group(1))
            if num > max_id:
                max_id = num
    
    return max_id + 1

def slugify(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    text = re.sub(r'\s+', '-', text)
    return text[:50]

def create_bug(data):
    bugs_dir = os.path.join(FEATURE_MGMT_DIR, "bugs")
    next_id = get_next_id("BUG", bugs_dir)
    bug_id = f"BUG-{next_id:03d}"
    slug = slugify(data['title'])
    item_dir = os.path.join(bugs_dir, f"{bug_id}-{slug}")
    
    os.makedirs(item_dir, exist_ok=True)
    
    # Metadata
    metadata = data.get('metadata', {})
    bug_json = {
        "bug_id": bug_id,
        "title": data['title'],
        "component": data['component'],
        "severity": metadata.get('severity', 'medium'),
        "priority": data['priority'],
        "status": "new",
        "reported_date": datetime.now().isoformat(),
        "description": data['description'],
        "steps_to_reproduce": metadata.get('steps_to_reproduce', []),
        "expected_behavior": metadata.get('expected_behavior', ''),
        "actual_behavior": metadata.get('actual_behavior', ''),
        "evidence": data.get('evidence', [])
    }
    
    with open(os.path.join(item_dir, "bug_report.json"), "w") as f:
        json.dump(bug_json, f, indent=2)
        
    # PROMPT.md
    with open(os.path.join(TEMPLATES_DIR, "bug_PROMPT.md.template"), "r") as f:
        template = f.read()
    
    content = template.format(
        ID=bug_id,
        title=data['title'],
        priority=data['priority'],
        component=data['component'],
        severity=metadata.get('severity', 'medium'),
        description=data['description'],
        evidence=json.dumps(data.get('evidence', []), indent=2),
        steps_to_reproduce=json.dumps(metadata.get('steps_to_reproduce', []), indent=2),
        expected_behavior=metadata.get('expected_behavior', ''),
        actual_behavior=metadata.get('actual_behavior', ''),
        root_cause=metadata.get('root_cause', 'To be determined'),
        notes=metadata.get('notes', '')
    )
    
    with open(os.path.join(item_dir, "PROMPT.md"), "w") as f:
        f.write(content)

    # Append to bugs.md
    bugs_md = os.path.join(FEATURE_MGMT_DIR, "bugs", "bugs.md")
    if os.path.exists(bugs_md):
        with open(bugs_md, "a") as f:
            f.write(f"| {bug_id} | {data['title']} | {data['priority']} | new | {data['component']} | [Link](bugs/{bug_id}-{slug}/) |\n")

    print(json.dumps({"success": True, "id": bug_id, "path": item_dir}))

def create_feature(data):
    feats_dir = os.path.join(FEATURE_MGMT_DIR, "features")
    next_id = get_next_id("FEAT", feats_dir)
    feat_id = f"FEAT-{next_id:03d}"
    slug = slugify(data['title'])
    item_dir = os.path.join(feats_dir, f"{feat_id}-{slug}")
    
    os.makedirs(item_dir, exist_ok=True)
    
    # Metadata
    metadata = data.get('metadata', {})
    feat_json = {
        "feature_id": feat_id,
        "title": data['title'],
        "component": data['component'],
        "priority": data['priority'],
        "status": "new",
        "type": metadata.get('type', 'enhancement'),
        "estimated_effort": metadata.get('estimated_effort', 'medium'),
        "description": data['description'],
        "business_value": metadata.get('business_value', 'medium')
    }
    
    with open(os.path.join(item_dir, "feature_request.json"), "w") as f:
        json.dump(feat_json, f, indent=2)
        
    # PROMPT.md
    with open(os.path.join(TEMPLATES_DIR, "feature_PROMPT.md.template"), "r") as f:
        template = f.read()
    
    content = template.format(
        ID=feat_id,
        title=data['title'],
        priority=data['priority'],
        component=data['component'],
        type=metadata.get('type', 'enhancement'),
        estimated_effort=metadata.get('estimated_effort', 'medium'),
        business_value=metadata.get('business_value', 'medium'),
        description=data['description'],
        benefits=metadata.get('benefits', ''),
        dependencies=metadata.get('dependencies', ''),
        notes=metadata.get('notes', '')
    )
    
    with open(os.path.join(item_dir, "PROMPT.md"), "w") as f:
        f.write(content)

    # Append to features.md
    feats_md = os.path.join(FEATURE_MGMT_DIR, "features", "features.md")
    if os.path.exists(feats_md):
        with open(feats_md, "a") as f:
            f.write(f"| {feat_id} | {data['title']} | {data['component']} | {data['priority']} | new | [Link](features/{feat_id}-{slug}/) |\n")

    print(json.dumps({"success": True, "id": feat_id, "path": item_dir}))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input_json", help="Path to input JSON file")
    args = parser.parse_args()
    
    with open(args.input_json, 'r') as f:
        data = json.load(f)
    
    if data['item_type'] == 'bug':
        create_bug(data)
    elif data['item_type'] == 'feature':
        create_feature(data)
    else:
        print(json.dumps({"success": False, "error": "Unknown item type"}))
