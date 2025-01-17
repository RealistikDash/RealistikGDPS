#!/bin/bash
set -euo pipefail

if [ -z "$APP_COMPONENT" ]; then
  echo "Please set APP_COMPONENT"
  exit 1
fi

if [ $APP_COMPONENT = "api" ]; then
  exec /app/scripts/run_api.sh
elif [ $APP_COMPONENT = "converter" ]; then
  exec /app/scripts/run_converter.sh
else
  echo "Unknown APP_COMPONENT: $APP_COMPONENT"
  exit 1
fi
