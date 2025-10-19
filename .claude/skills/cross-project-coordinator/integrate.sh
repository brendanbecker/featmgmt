#!/bin/bash

# Cross-Project Coordinator Integration Script
set -e

SKILL_DIR="$(dirname "$0")"
ACTION="${1:-status}"

echo "🌐 Cross-Project Coordinator v1.0.0"
echo "===================================="

case "$ACTION" in
    discover)
        echo "🔍 Discovering projects..."
        python3 "$SKILL_DIR/scripts/project_registry.py"
        ;;

    status)
        echo "📊 Project Portfolio Status:"
        python3 "$SKILL_DIR/scripts/portfolio_status.py"
        ;;

    impact)
        PROJECT="${2}"
        if [ -z "$PROJECT" ]; then
            echo "❌ Error: Project name required"
            echo "Usage: $0 impact <project>"
            exit 1
        fi
        echo "📈 Analyzing impact for $PROJECT..."
        python3 "$SKILL_DIR/scripts/impact_analyzer.py" --project "$PROJECT"
        ;;

    dependencies)
        echo "🔗 Analyzing dependencies..."
        python3 "$SKILL_DIR/scripts/dependency_analyzer.py"
        ;;

    release)
        echo "🚀 Planning coordinated release..."
        python3 "$SKILL_DIR/scripts/release_coordinator.py" --plan
        ;;

    dashboard)
        echo "🖥️ Starting dashboard on port 8888..."
        python3 "$SKILL_DIR/scripts/dashboard_server.py"
        ;;

    sync)
        echo "🔄 Synchronizing project states..."
        python3 "$SKILL_DIR/scripts/sync_projects.py"
        ;;

    report)
        echo "📄 Generating cross-project report..."
        python3 "$SKILL_DIR/scripts/generate_report.py"
        ;;

    *)
        echo "❌ Unknown action: $ACTION"
        echo "Available actions: discover, status, impact, dependencies, release, dashboard, sync, report"
        exit 1
        ;;
esac

echo ""
echo "✅ Coordination action complete!"
