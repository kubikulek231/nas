#!/usr/bin/env bash
set -euo pipefail

TARGET_DIR="/srv/website"
SERVICE_NAME="nashub-website.service"

echo "[deploy] Syncing files to ${TARGET_DIR} ..."

# Create target dir if missing
sudo mkdir -p "${TARGET_DIR}"

# Sync current directory contents into TARGET_DIR
# Adjust excludes as needed.
sudo rsync -av \
  --delete \
  ./ "${TARGET_DIR}/"

echo "[deploy] Setting ownership (nas:nas) ..."
sudo chown -R nas:nas "${TARGET_DIR}"

echo "[deploy] Restarting service ${SERVICE_NAME} ..."
sudo systemctl restart "${SERVICE_NAME}"
sudo systemctl status "${SERVICE_NAME}" --no-pager --lines=5

echo "[deploy] Done."