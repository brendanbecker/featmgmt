#!/bin/bash
# run_tests.sh
# Runs tests for a specific component

COMPONENT=$1

if [[ -z "$COMPONENT" ]]; then
    echo "Usage: ./run_tests.sh [backend|frontend|discord]"
    exit 1
fi

# Common env vars
export DATABASE_URL="postgresql://postgres:postgres@192.168.7.17:5432/triager_test"
export TEST_MODE=true

./scripts/verify_db_safety.sh

if [[ "$COMPONENT" == "backend" ]]; then
    echo "Running backend tests..."
    cd /home/becker/projects/triager/backend
    source .venv/bin/activate
    python -m pytest -v
elif [[ "$COMPONENT" == "frontend" ]]; then
    echo "Running frontend tests..."
    cd /home/becker/projects/triager/website
    export REACT_APP_API_URL="http://192.168.7.17:8800"
    npm test -- --watchAll=false
elif [[ "$COMPONENT" == "discord" ]]; then
    echo "Running discord bot tests..."
    cd /home/becker/projects/triager/discord-bot
    source .venv/bin/activate
    export API_BASE_URL="http://192.168.7.17:8800"
    python -m pytest -v
else
    echo "Unknown component: $COMPONENT"
    exit 1
fi
