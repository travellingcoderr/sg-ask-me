#!/bin/bash
# Check PostgreSQL data
# Usage: ./scripts/check-postgres.sh

echo "=== PostgreSQL Databases ==="
docker compose exec postgres psql -U app -c "\l"

echo ""
echo "=== Tables in chatdb ==="
docker compose exec postgres psql -U app -d chatdb -c "\dt"

echo ""
echo "=== Table Sizes ==="
docker compose exec postgres psql -U app -d chatdb -c "
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
"

echo ""
echo "=== Connection Info ==="
docker compose exec postgres psql -U app -d chatdb -c "SELECT version();"
