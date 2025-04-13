#!/usr/bin/env bash
set -euo pipefail

if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

if [ -z "$APP_COMPONENT" ]; then
  echo "Please set APP_COMPONENT"
  exit 1
fi

case $APP_COMPONENT in
  "bot")
    exec scripts/run_bot.sh
    ;;

  *)
    echo "'$APP_COMPONENT' isn't a known value for APP_COMPONENT"
    ;;
esac
