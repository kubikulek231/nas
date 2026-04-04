Go back to [Index](./../README.md)

# Website (Python Flask)

- Goal is to serve a simple website hub featuring what our NAS can do. 


1. Install python3, pip and flask
    ```bash
    # Setup Python Repo
    sudo apt install software-properties-common
    sudo add-apt-repository ppa:deadsnakes/ppa

    # Install Python 3.x and venv module
    sudo apt install -y python3.13 python3.13-venv

    # Create a venv in /home/nas/.venv
    python3.13 -m venv /home/nas/.venv

    # Activate it
    source /home/nas/.venv/bin/activate

    # Install Flask and Gunicorn into the venv
    pip install Flask gunicorn

    # Install zpool-status into the venv
    pip install zpool-status
    ```

2. Copy the contents of `src/` from this repository directory to `/srv/website` and create a persistent history directory at `/home/nas/nas/data/drive-status`:

    ```bash
    # Set permissions
    sudo chown -R nas:nas /srv/website
    sudo chmod -R u+rwX,go+rX /srv/website
    sudo mkdir -p /home/nas/nas/data/drive-status
    sudo chown -R nas:nas /home/nas/nas/data/drive-status
    ```

    Now the `python3 app.py` can be run and the website can be developed.

3. Setup production website:

    Allow gunicorn to access the usual HTTP (80) port:
    ```bash
    sudo setcap 'cap_net_bind_service=+ep' /home/nas/.venv/bin/gunicorn
    ```

    Create the systemd webserver service by using:
    ```bash
    sudo nano /etc/systemd/system/nashub-website.service
    ```
    And pasting contents of `nashub-website.service` next to this readme file in.

4. Starting the systemd service and timer:
    ```bash
    sudo systemctl daemon-reload
    sudo systemctl enable nashub-website.service
    sudo systemctl enable nashub-monitor-drives.timer
    sudo systemctl start nashub-website.service
    sudo systemctl start nashub-monitor-drives.timer
    sudo systemctl status nashub-website.service
    sudo systemctl status nashub-monitor-drives.timer
    ```
    The drive history collector now runs through a systemd timer every 5 minutes, which keeps logs in journalctl and avoids managing a root crontab entry manually.

    Or if this whole repository is cloned via git, run `chmod +x ./deploy.sh` and then `./deploy.sh` from inside the website directory.