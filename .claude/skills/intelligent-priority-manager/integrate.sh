#!/bin/bash

# Integration script for Intelligent Priority Manager Skill
# This replaces the scan-prioritize-agent in OVERPROMPT workflows

set -e

SKILL_DIR="$(dirname "$0")"
FEATURE_DIR="${1:-./feature-management}"

echo "🧠 Intelligent Priority Manager v1.0.0"
echo "======================================"

# Run dependency analysis
echo "📊 Analyzing dependencies..."
python3 "$SKILL_DIR/scripts/analyze_dependencies.py" "$FEATURE_DIR" > /tmp/dependencies.json

# Run pattern recognition
echo "🔍 Analyzing historical patterns..."
python3 "$SKILL_DIR/scripts/pattern_recognition.py" "$FEATURE_DIR/completed" > /tmp/patterns.json

# Calculate priorities
echo "🎯 Calculating priorities..."
python3 "$SKILL_DIR/scripts/calculate_priority.py" \
  --config "$SKILL_DIR/resources/priority_config.json" \
  --dependencies /tmp/dependencies.json \
  --patterns /tmp/patterns.json \
  --output /tmp/priorities.json

# Generate report
echo "📝 Generating priority report..."
python3 "$SKILL_DIR/scripts/generate_report.py" \
  --template "$SKILL_DIR/templates/priority_report.md" \
  --data /tmp/priorities.json \
  --output "$FEATURE_DIR/agent_runs/priority_report_$(date +%Y%m%d_%H%M%S).md"

# Output top items for immediate action
echo ""
echo "🎯 Top Priority Items:"
python3 -c "
import json
with open('/tmp/priorities.json') as f:
    data = json.load(f)
    for item in data['items'][:5]:
        print(f\"  • {item['id']}: {item['title']} (Score: {item['priority_score']:.1f})\")
"

echo ""
echo "✅ Priority analysis complete!"
