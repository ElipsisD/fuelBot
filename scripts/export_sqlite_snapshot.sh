#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

SOURCE_DB="${1:-${PROJECT_ROOT}/data/fuelbot.sqlite3}"
TARGET_DB="${2:-/mnt/c/Temp/fuelbot-snapshot.sqlite3}"

if ! command -v sqlite3 >/dev/null 2>&1; then
  echo "sqlite3 is not installed" >&2
  exit 1
fi

if [[ ! -f "${SOURCE_DB}" ]]; then
  echo "source database not found: ${SOURCE_DB}" >&2
  exit 1
fi

TARGET_DIR="$(dirname "${TARGET_DB}")"
mkdir -p "${TARGET_DIR}"

echo "Creating SQLite snapshot"
echo "  source: ${SOURCE_DB}"
echo "  target: ${TARGET_DB}"

sqlite3 "${SOURCE_DB}" ".backup ${TARGET_DB}"

echo "Snapshot ready: ${TARGET_DB}"
