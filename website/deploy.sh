#!/usr/bin/env bash
set -euo pipefail

TARGET_DIR="/srv/website"
DATA_DIR="/home/nas/nas/data/drive-status"
WEBSITE_SERVICE_NAME="nashub-website.service"
MONITOR_SERVICE_NAME="nashub-monitor-drives.service"
MONITOR_TIMER_NAME="nashub-monitor-drives.timer"
SYSTEMD_DIR="/etc/systemd/system"

echo "[deploy] Syncing files to ${TARGET_DIR} ..."

sudo mkdir -p "${TARGET_DIR}"
sudo mkdir -p "${DATA_DIR}"

sudo rsync -av \
  --delete \
  --exclude='[0-9][0-9][0-9][0-9]-[0-9][0-9].json' \
  ./src/ "${TARGET_DIR}"

echo "[deploy] Setting ownership (nas:nas) on runtime paths ..."
sudo chown -R nas:nas "${TARGET_DIR}"
sudo chown -R nas:nas "${DATA_DIR}"

echo "[deploy] Installing systemd units ..."
sudo cp "${WEBSITE_SERVICE_NAME}" "${SYSTEMD_DIR}/${WEBSITE_SERVICE_NAME}"
sudo cp "${MONITOR_SERVICE_NAME}" "${SYSTEMD_DIR}/${MONITOR_SERVICE_NAME}"
sudo cp "${MONITOR_TIMER_NAME}" "${SYSTEMD_DIR}/${MONITOR_TIMER_NAME}"

echo "[deploy] Reloading systemd daemon ..."
sudo systemctl daemon-reload

echo "[deploy] Enabling website service and drive monitor timer ..."
sudo systemctl enable "${WEBSITE_SERVICE_NAME}" "${MONITOR_TIMER_NAME}"

echo "[deploy] Removing legacy cron job if present ..."
CRON_CONTENT=$(sudo crontab -l 2>/dev/null || true)
FILTERED_CRON=$(printf '%s\n' "$CRON_CONTENT" | grep -v "monitor_drives.py" || true)
if [ "$CRON_CONTENT" != "$FILTERED_CRON" ]; then
  printf '%s\n' "$FILTERED_CRON" | sudo crontab -
fi

echo "[deploy] Running an immediate drive status collection ..."
sudo systemctl start "${MONITOR_SERVICE_NAME}"

echo "[deploy] Restarting service ${WEBSITE_SERVICE_NAME} ..."
sudo systemctl restart "${WEBSITE_SERVICE_NAME}"
sudo systemctl restart "${MONITOR_TIMER_NAME}"

echo "[deploy] You can view lastly logged by 'sudo journalctl -u nashub-website.service -n 50 --no-pager -f'"

echo "[deploy] Sleeping for 5 seconds..."
sleep 5

sudo systemctl status "${WEBSITE_SERVICE_NAME}" --no-pager --lines=5
sudo systemctl status "${MONITOR_TIMER_NAME}" --no-pager --lines=5

echo "[deploy] Done."
