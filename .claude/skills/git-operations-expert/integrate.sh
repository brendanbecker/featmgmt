#!/bin/bash

# Git Operations Expert Skill Integration Script
set -e

SKILL_DIR="$(dirname "$0")"
ACTION="${1:-commit}"

echo "🔀 Git Operations Expert v1.0.0"
echo "================================"

case "$ACTION" in
    commit)
        echo "📝 Generating commit message..."
        MESSAGE=$(python3 "$SKILL_DIR/scripts/commit_generator.py")
        echo "$MESSAGE"
        echo ""
        read -p "Use this commit message? (y/n/e to edit): " response

        case $response in
            y|Y)
                git commit -m "$MESSAGE"
                echo "✅ Committed successfully"
                ;;
            e|E)
                echo "$MESSAGE" > /tmp/commit_msg.txt
                ${EDITOR:-nano} /tmp/commit_msg.txt
                git commit -F /tmp/commit_msg.txt
                echo "✅ Committed with edited message"
                ;;
            *)
                echo "Commit cancelled"
                ;;
        esac
        ;;

    resolve)
        echo "🔧 Detecting conflicts..."
        python3 "$SKILL_DIR/scripts/conflict_resolver.py"
        ;;

    pr)
        echo "🚀 Creating pull request..."
        python3 "$SKILL_DIR/scripts/pr_creator.py"
        ;;

    status)
        echo "📊 Repository status:"
        git status
        echo ""
        echo "📈 Recent commits:"
        git log --oneline -5
        ;;

    *)
        echo "❌ Unknown action: $ACTION"
        echo "Available actions: commit, resolve, pr, status"
        exit 1
        ;;
esac
