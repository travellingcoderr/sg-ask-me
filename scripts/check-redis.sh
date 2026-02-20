#!/bin/bash
# Check Redis data
# Usage: ./scripts/check-redis.sh

echo "=== Redis Keys ==="
docker compose exec redis redis-cli KEYS "*"

echo ""
echo "=== All Rate Limit Keys ==="
docker compose exec redis redis-cli KEYS "rl:*"

echo ""
echo "=== Sample Rate Limit Data ==="
FIRST_KEY=$(docker compose exec -T redis redis-cli KEYS "rl:*" | head -1)
if [ -n "$FIRST_KEY" ]; then
  echo "Key: $FIRST_KEY"
  docker compose exec redis redis-cli ZRANGE "$FIRST_KEY" 0 -1 WITHSCORES
  echo "Count: $(docker compose exec -T redis redis-cli ZCARD "$FIRST_KEY")"
fi

echo ""
echo "=== Redis Info ==="
docker compose exec redis redis-cli INFO stats
