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
    ```
2. Copy app.py, index.html and style.css from this repository directory to `/srv/website` and:

    ```bash
    # Set permissions
    sudo chown -R nas:nas /srv/website
    sudo chmod -R u+rwX,go+rX /srv/website
    ```