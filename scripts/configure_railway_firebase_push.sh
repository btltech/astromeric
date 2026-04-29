#!/usr/bin/env bash

set -euo pipefail

PROJECT_ID="${1:-astromeric-260422-f3f5}"
SERVICE_ACCOUNT_PATH="${2:-}"

if ! command -v railway >/dev/null 2>&1; then
    echo "Railway CLI is required. Install it first."
    exit 1
fi

echo "Setting FIREBASE_PROJECT_ID on the linked Railway service..."
railway variable set "FIREBASE_PROJECT_ID=${PROJECT_ID}"

if [[ -n "${SERVICE_ACCOUNT_PATH}" ]]; then
    if [[ ! -f "${SERVICE_ACCOUNT_PATH}" ]]; then
        echo "Service account file not found: ${SERVICE_ACCOUNT_PATH}"
        exit 1
    fi

    echo "Uploading FIREBASE_SERVICE_ACCOUNT_JSON from ${SERVICE_ACCOUNT_PATH} ..."
    python3 - <<'PY' "${SERVICE_ACCOUNT_PATH}" | railway variable set --stdin FIREBASE_SERVICE_ACCOUNT_JSON
import json
import pathlib
import sys

path = pathlib.Path(sys.argv[1])
payload = json.loads(path.read_text())
print(json.dumps(payload, separators=(",", ":")))
PY

    echo "Firebase Admin credentials uploaded to Railway."
else
    cat <<EOF
FIREBASE_PROJECT_ID is now set.

To finish backend FCM delivery, generate or download a Firebase Admin service account JSON
for project ${PROJECT_ID}, then rerun:

  ./scripts/configure_railway_firebase_push.sh ${PROJECT_ID} /absolute/path/to/service-account.json

That will set FIREBASE_SERVICE_ACCOUNT_JSON on the linked Railway service.
EOF
fi