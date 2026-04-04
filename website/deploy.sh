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

echo "[deploy] Setting up drive monitoring cron job ..."
# Get current crontab content, or empty if none exists
CRON_CONTENT=$(sudo crontab -l 2>/dev/null || echo "")
if echo "$CRON_CONTENT" | grep -q "monitor_drives.py"; then
    echo "[deploy] Cron job already exists, skipping..."
else
    echo "[deploy] Adding cron job..."
    (echo "$CRON_CONTENT"; echo "*/5 * * * * /usr/bin/python3 ${TARGET_DIR}/monitor_drives.py") | sudo crontab -
fi

echo "[deploy] You can view lastly logged by 'sudo journalctl -u nashub-website.service -n 50 --no-pager -f'"

echo "[deploy] Sleeping for 5 seconds..."
sleep 5

sudo systemctl status "${SERVICE_NAME}" --no-pager --lines=5

echo "[deploy] Done."
