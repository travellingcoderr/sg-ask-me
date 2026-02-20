#!/bin/bash
# Interactive PostgreSQL CLI
# Usage: ./scripts/psql.sh

docker compose exec postgres psql -U app -d chatdb
