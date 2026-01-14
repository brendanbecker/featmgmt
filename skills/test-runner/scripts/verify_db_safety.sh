#!/bin/bash
set -e

# verify_db_safety.sh
# Ensures we are not running against production

if [[ -z "$DATABASE_URL" ]]; then
    echo "Error: DATABASE_URL is not set."
    exit 1
fi

echo "Verifying database safety..."
echo "DATABASE_URL: $DATABASE_URL"

if [[ "$DATABASE_URL" == *"triager"* ]] && [[ "$DATABASE_URL" != *"triager_test"* ]]; then
  echo "❌ ERROR: Cannot run tests against production database!"
  exit 1
fi

echo "✅ Database safety check passed."
