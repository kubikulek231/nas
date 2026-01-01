Go back to [Index](./../README.md)

# Website (Python Flask)

- Goal is to serve a simple website hub featuring what our NAS can do. 


1. Install python3, pip and flask
    ```bash
    # Setup Python Repo
    sudo apt install software-properties-common
    sudo add-apt-repository ppa:deadsnakes/ppa
    # Install Python
    sudo apt install python3.13
    # Install System-Wide Flask
    sudo apt install python3-flask
    pip install gunicorn
    ```

2. Copy app.py, index.html and style.css from this repository directory to `/srv/website` and:

    ```bash
    # Set permissions
    sudo chown -R nas:nas /srv/website
    sudo chmod -R u+rwX,go+rX /srv/website
    ```

    Now the `python3 app.py` can be run and the website can be developed.

3. Setup production website:

    Install gunicorn system-wide:
    ```bash
    sudo apt install gunicorn
    ```

    Allow gunicorn to access the usual HTTP (80) port:
    ```bash
    sudo setcap 'cap_net_bind_service=+ep' /usr/bin/gunicorn
    ```

    Create the systemd webserver service by using:
    ```bash
    sudo nano /etc/systemd/system/nashub-website.service
    ```
    And pasting contents of `nashub-website.service` next to this readme file in.

4. Starting the systemd service:
    ```bash
    sudo systemctl daemon-reload
    sudo systemctl enable nashub-website.service
    sudo systemctl start nashub-website.service
    sudo systemctl status nashub-website.service
    ```
    Or if this whole repository is cloned via git, just run the do `chmod +x ./deploy` and run ./deploy from inside the website dir.