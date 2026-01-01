#!/usr/bin/env bash
set -euo pipefail

TARGET_DIR="/srv/website"
SERVICE_NAME="nashub-website.service"
SERVICE_PATH="/etc/systemd/system/${SERVICE_NAME}"

echo "[deploy] Syncing files to ${TARGET_DIR} ..."

# Create target dir if missing
sudo mkdir -p "${TARGET_DIR}"

# Sync current directory contents into TARGET_DIR
sudo rsync -av \
  --delete \
  ./src/ "${TARGET_DIR}"

echo "[deploy] Setting ownership (nas:nas) ..."
sudo chown -R nas:nas "${TARGET_DIR}"

echo "[deploy] Installing systemd service ${SERVICE_NAME} ..."
sudo cp "${SERVICE_NAME}" "${SERVICE_PATH}"

echo "[deploy] Reloading systemd daemon ..."
sudo systemctl daemon-reload   # required after changing unit files[web:92][web:127][web:130]

echo "[deploy] Restarting service ${SERVICE_NAME} ..."
sudo systemctl restart "${SERVICE_NAME}"
sudo systemctl status "${SERVICE_NAME}" --no-pager --lines=5

echo "[deploy] Done."
