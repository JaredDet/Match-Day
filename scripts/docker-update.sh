#!/usr/bin/env sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
COMPOSE_FILE="$SCRIPT_DIR/../docker-compose.yml"

docker compose -f "$COMPOSE_FILE" build
docker compose -f "$COMPOSE_FILE" up -d --wait postgres redis
docker compose -f "$COMPOSE_FILE" run --rm initialize
if [ "${SEED_DEMO:-0}" = "1" ]; then
  docker compose -f "$COMPOSE_FILE" --profile demo run --rm seed-demo
fi
docker compose -f "$COMPOSE_FILE" up -d --force-recreate --wait \
  backend match-clock-worker news-worker recommendations-worker frontend
docker compose -f "$COMPOSE_FILE" ps

printf '%s\n' "Matchday actualizado en http://localhost:3000"
