#!/bin/bash
set -e

# setup_test_db.sh
# Sets up and cleans the triager_test database

DB_HOST="192.168.7.17"
DB_PORT="5432"
DB_USER="postgres"
TEST_DB="triager_test"

echo "Checking test database connection..."
# Check if test database exists
if ! psql -h $DB_HOST -p $DB_PORT -U $DB_USER -lqt | grep -qw $TEST_DB; then
    echo "Creating database $TEST_DB..."
    psql -h $DB_HOST -p $DB_PORT -U $DB_USER -c "CREATE DATABASE $TEST_DB;"
else
    echo "Database $TEST_DB exists."
fi

echo "Cleaning test database (preserving schema)..."
psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $TEST_DB -c "
DO \$\$
DECLARE
  r RECORD;
BEGIN
  FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = 'public') LOOP
    EXECUTE 'TRUNCATE TABLE ' || quote_ident(r.tablename) || ' CASCADE;';
  END LOOP;
END \$\$;"

echo "Test database setup complete."
