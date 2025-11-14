#!/bin/bash

# Path to the .env file (one level up from script location)
ENV_PATH="$(dirname "$0")/../.env"

# Export variables from the specified .env file
if [ -f "$ENV_PATH" ]; then
    export $(grep -v '^#' "$ENV_PATH" | xargs)
else
    echo "Error: .env file not found at $ENV_PATH"
    exit 1
fi

# Run Telegraf
telegraf --config telegraf.conf
