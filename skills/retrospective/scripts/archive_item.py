#!/usr/bin/env python3
import os
import json
import shutil
import argparse
from datetime import datetime

# Paths
BASE_DIR = os.getcwd()
FEATURE_MGMT_DIR = os.path.join(BASE_DIR, "feature-management")

def archive_item(item_path, reason, status="completed", superseded_by=None):
    if not os.path.exists(item_path):
        print(json.dumps({"success": False, "error": f"Path not found: {item_path}"}))
        return

    item_name = os.path.basename(item_path)
    item_type = "bugs" if "bugs" in item_path else "features"
    if "features" not in item_path and "bugs" not in item_path:
         # Try to guess or fail
         pass

    # Determine destination
    dest_dir = os.path.join(FEATURE_MGMT_DIR, "completed" if status == "completed" else "deprecated")
    os.makedirs(dest_dir, exist_ok=True)
    dest_path = os.path.join(dest_dir, item_name)

    # Update metadata
    json_file = os.path.join(item_path, "bug_report.json" if "bugs" in item_path else "feature_request.json")
    if os.path.exists(json_file):
        with open(json_file, 'r') as f:
            data = json.load(f)
        
        data['status'] = status
        data[f'{status}_date'] = datetime.now().isoformat()
        data[f'{status}_reason'] = reason
        if superseded_by:
            data['superseded_by'] = superseded_by
            
        with open(json_file, 'w') as f:
            json.dump(data, f, indent=2)

    # Move directory
    try:
        shutil.move(item_path, dest_path)
        print(json.dumps({"success": True, "path": dest_path}))
    except Exception as e:
        print(json.dumps({"success": False, "error": str(e)}))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("path", help="Path to item directory")
    parser.add_argument("--reason", required=True, help="Reason for archiving")
    parser.add_argument("--status", choices=["completed", "deprecated", "merged"], default="completed")
    parser.add_argument("--superseded-by", help="ID of superseding item")
    
    args = parser.parse_args()
    archive_item(args.path, args.reason, args.status, args.superseded_by)
