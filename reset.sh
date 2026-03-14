#!/usr/bin/env bash
read -p "Are you sure you want to reset and delete all volumes? [y/N]: " response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    docker compose down -v
else
    echo "Reset aborted."
fi
