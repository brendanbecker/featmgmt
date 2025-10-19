#!/bin/bash

# Integration script for Stateful Workflow Orchestrator
# Replaces sequential OVERPROMPT execution with stateful, parallel workflow

set -e

SKILL_DIR="$(dirname "$0")"
WORKFLOW_TYPE="${1:-standard}"
ACTION="${2:-run}"  # run, resume, status, dashboard

echo "🔄 Stateful Workflow Orchestrator v1.0.0"
echo "========================================="

case "$ACTION" in
    run)
        echo "▶️  Starting new workflow..."
        python3 "$SKILL_DIR/scripts/orchestrate.py" \
            --config "$SKILL_DIR/resources/workflow_config.yaml" \
            --type "$WORKFLOW_TYPE" \
            --action start
        ;;

    resume)
        WORKFLOW_ID="${3}"
        if [ -z "$WORKFLOW_ID" ]; then
            echo "❌ Error: Workflow ID required for resume"
            echo "Usage: $0 $WORKFLOW_TYPE resume <workflow_id>"
            exit 1
        fi
        echo "▶️  Resuming workflow $WORKFLOW_ID..."
        python3 "$SKILL_DIR/scripts/orchestrate.py" \
            --config "$SKILL_DIR/resources/workflow_config.yaml" \
            --workflow-id "$WORKFLOW_ID" \
            --action resume
        ;;

    status)
        echo "📊 Workflow Status:"
        python3 "$SKILL_DIR/scripts/orchestrate.py" \
            --action status
        ;;

    dashboard)
        echo "🖥️  Opening workflow dashboard..."
        python3 "$SKILL_DIR/scripts/orchestrate.py" \
            --action dashboard \
            --port 8080
        echo "Dashboard available at http://localhost:8080"
        ;;

    *)
        echo "❌ Unknown action: $ACTION"
        echo "Available actions: run, resume, status, dashboard"
        exit 1
        ;;
esac

echo ""
echo "✅ Orchestrator action complete!"
