#!/bin/bash
set -e

ENV_PATH="$(dirname "$0")/../.env"

if [ ! -f "$ENV_PATH" ]; then
  echo "Error: .env not found at $ENV_PATH"
  exit 1
fi

# Export env vars
set -a
source "$ENV_PATH"
set +a

# Run telegraf in foreground
exec telegraf --config "$(dirname "$0")/telegraf.conf"

