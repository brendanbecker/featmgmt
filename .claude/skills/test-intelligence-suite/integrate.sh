#!/bin/bash

# Test Intelligence Suite Integration Script
set -e

SKILL_DIR="$(dirname "$0")"
ACTION="${1:-smart}"
TEST_PATH="${2:-.}"

echo "🧪 Test Intelligence Suite v1.0.0"
echo "=================================="

case "$ACTION" in
    smart)
        echo "🎯 Running smart test selection..."

        # Get changed files
        CHANGED_FILES=$(git diff --name-only HEAD~1 2>/dev/null || echo "")

        if [ -z "$CHANGED_FILES" ]; then
            echo "No changes detected, running smoke tests only"
            python3 "$SKILL_DIR/scripts/run_tests.py" --smoke
        else
            echo "Analyzing impact of changes..."
            echo "$CHANGED_FILES" | python3 "$SKILL_DIR/scripts/impact_analyzer.py"

            # Run affected tests
            python3 "$SKILL_DIR/scripts/run_tests.py" --smart
        fi
        ;;

    parallel)
        echo "⚡ Running tests in parallel..."
        python3 "$SKILL_DIR/scripts/parallel_executor.py" "$TEST_PATH"
        ;;

    flaky)
        echo "🔍 Analyzing flaky tests..."
        python3 "$SKILL_DIR/scripts/flaky_detector.py" --report
        ;;

    coverage)
        echo "📊 Analyzing test coverage..."
        coverage run -m pytest "$TEST_PATH"
        coverage report
        coverage html
        echo "Coverage report generated in htmlcov/"
        ;;

    full)
        echo "🏃 Running full test suite..."
        python3 "$SKILL_DIR/scripts/run_tests.py" --all
        ;;

    quarantine)
        echo "🔒 Managing quarantined tests..."
        python3 "$SKILL_DIR/scripts/flaky_detector.py" --quarantine
        ;;

    report)
        echo "📈 Generating test intelligence report..."
        python3 "$SKILL_DIR/scripts/generate_report.py"
        ;;

    *)
        echo "❌ Unknown action: $ACTION"
        echo "Available actions: smart, parallel, flaky, coverage, full, quarantine, report"
        exit 1
        ;;
esac

echo ""
echo "✅ Test execution complete!"

# Generate summary
python3 -c "
import json
import sqlite3

conn = sqlite3.connect('test_history.db')
cursor = conn.cursor()

cursor.execute('''
    SELECT COUNT(*), SUM(passed), MAX(run_date)
    FROM test_runs
    WHERE date(run_date) = date('now')
''')

total, passed, last_run = cursor.fetchone()

if total:
    pass_rate = (passed / total * 100) if passed else 0
    print(f'📊 Today\'s Summary:')
    print(f'   Tests run: {total}')
    print(f'   Pass rate: {pass_rate:.1f}%')
    print(f'   Last run: {last_run}')
"
