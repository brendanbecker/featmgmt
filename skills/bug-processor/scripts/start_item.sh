#!/bin/bash
# start_item.sh
# Marks an item as in_progress and commits the change

ITEM_PATH=$1

if [[ -z "$ITEM_PATH" ]]; then
    echo "Usage: ./start_item.sh <path_to_item_directory>"
    exit 1
fi

REPORT_FILE="$ITEM_PATH/bug_report.json"
if [[ ! -f "$REPORT_FILE" ]]; then
    REPORT_FILE="$ITEM_PATH/feature_request.json"
fi

if [[ ! -f "$REPORT_FILE" ]]; then
    echo "Error: Could not find report json in $ITEM_PATH"
    exit 1
fi

# Use python to update json safely
python3 -c "
import json, sys, datetime
file_path = '$REPORT_FILE'
try:
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    data['status'] = 'in_progress'
    data['updated_date'] = datetime.date.today().isoformat()
    if 'started_date' not in data:
        data['started_date'] = datetime.date.today().isoformat()
        
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)
    print(f'Updated {file_path}')
except Exception as e:
    print(f'Error updating json: {e}')
    sys.exit(1)
"

# Commit the change
ITEM_ID=$(basename "$ITEM_PATH" | cut -d'-' -f1-2)
git add "$REPORT_FILE"
git commit -m "chore($ITEM_ID): Mark as in_progress"

echo "Marked $ITEM_ID as in_progress"
