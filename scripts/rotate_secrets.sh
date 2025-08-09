#!/bin/bash
# Secret Rotation Helper
# Usage: ./scripts/rotate_secrets.sh .env.production
set -euo pipefail

ENV_FILE="${1:-.env.production}"
TMP_FILE="${ENV_FILE}.rotating.$$"
DATE_TAG=$(date -u +%Y%m%dT%H%M%SZ)

rand() {
  # 48 bytes -> base64 -> strip non-alnum for simplicity
  openssl rand -base64 48 | tr -dc 'A-Za-z0-9' | head -c 64
}

if [ ! -f "$ENV_FILE" ]; then
  echo "[ERROR] Environment file $ENV_FILE not found" >&2
  exit 1
fi

cp "$ENV_FILE" "$TMP_FILE"

rotate_var() {
  local var="$1"
  if grep -q "^${var}=" "$TMP_FILE"; then
    local newval
    newval=$(rand)
    sed -i "s#^${var}=.*#${var}=${newval}#" "$TMP_FILE"
    echo "[ROTATED] ${var}"
  else
    echo "[MISSING] ${var} (adding)" >&2
    echo "${var}=$(rand)" >> "$TMP_FILE"
  fi
}

# Core secrets to rotate
rotate_var JWT_SECRET_KEY
rotate_var API_SECRET_KEY
rotate_var POSTGRES_PASSWORD
rotate_var REDIS_PASSWORD
rotate_var GRAFANA_PASSWORD

# Annotate rotation metadata
if grep -q '^# LastSecretRotation:' "$TMP_FILE"; then
  sed -i "s/^# LastSecretRotation:.*/# LastSecretRotation: ${DATE_TAG}/" "$TMP_FILE"
else
  echo "# LastSecretRotation: ${DATE_TAG}" >> "$TMP_FILE"
fi

# Preserve original as backup
cp "$ENV_FILE" "${ENV_FILE}.backup-${DATE_TAG}"

mv "$TMP_FILE" "$ENV_FILE"

echo "[DONE] Secrets rotated. Backup saved as ${ENV_FILE}.backup-${DATE_TAG}"
