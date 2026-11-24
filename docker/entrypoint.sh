#!/bin/sh
# Start-up script for the PostPix API container.
#
#   RUN_MIGRATIONS=1  run `flask db upgrade` before starting (default: off;
#                     production runs migrations as a separate deploy step,
#                     after a database snapshot)
#   SEED_ON_START=1   run `flask seed all` before starting (default: off;
#                     safe: it only seeds an EMPTY database)
#
# Then it replaces itself with the command (gunicorn by default), so the
# server is PID 1 and receives Docker's stop signal directly.
set -eu

is_on() {
  case "${1:-}" in
    1|true|TRUE|True|yes|on) return 0 ;;
    *) return 1 ;;
  esac
}

if is_on "${RUN_MIGRATIONS:-0}"; then
  echo "entrypoint: flask db upgrade"
  flask db upgrade
fi

if is_on "${SEED_ON_START:-0}"; then
  echo "entrypoint: flask seed all (only seeds an empty database)"
  flask seed all
fi

exec "$@"
