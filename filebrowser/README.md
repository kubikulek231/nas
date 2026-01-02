Go back to [Index](./../README.md)

### FileBrowser Quantum

This file provides guidance on how FileBrowser Quantum tool for browsing the NAS files using plain browser from given ip address is set up.

Any user within the network can access any files from any device 📱💻 easilly from this place.

### Set-up steps

1. Download and extract filebrowser binary from https://github.com/gtsteffaniak/filebrowser/releases to `/opt/filebrowser` and place the binary in `/usr/local/bin`.
   ```bash
   # Go to https://github.com/gtsteffaniak/filebrowser/releases and get exact link by right clicking correct file and copying it.
   # Linux AMD64
   sudo mkdir -p /opt/filebrowser
   # Download the binary
   sudo wget https://github.com/gtsteffaniak/filebrowser/releases/download/v1.1.0-stable/linux-amd64-filebrowser -O /usr/local/bin/filebrowser

   # Make it runnable
   sudo chmod +x /usr/local/bin/filebrowser
   ```
2. Install FFmpeg
   ```bash
   sudo apt install ffmpeg
   ```

3. Set-up Filebrowser config at `/opt/filebrowser/config.yaml`
   ```bash
   sudo nano /opt/filebrowser/config.yaml
   ```

   Paste following or use the full config `config.yaml` next to this README:

   ```yml
   server:
   sources:
      - path: "/srv/data"
         config:
         defaultEnabled: true  
         # Give access to all users by default

   auth:
   adminUsername: admin
   adminPassword: admin
   ```

3. Create service user and DB dir
   ```bash
   sudo useradd filebrowser
   sudo mkdir -p /opt/filebrowser
   sudo chown filebrowser:filebrowser /opt/filebrowser

   sudo usermod -aG sudo filebrowser
   ```

4. Configure
   ```bash
   sudo chown filebrowser:filebrowser /opt/filebrowser/config.yaml
   sudo chown filebrowser:filebrowser /opt/filebrowser/
   sudo chown filebrowser:filebrowser /opt/filebrowser/filebrowser

   # Set up admin password
   FILEBROWSER_ADMIN_PASSWORD="mysecurePassword"
   ```

3. Create systemd service. A file for running the filebrowser as service needs to be created. One can use nano:
   ```bash
   sudo nano /etc/systemd/system/filebrowser.service
   ```
   And copy and save contents of the file available next to this README.

4. Start the daemon
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable filebrowser
   sudo systemctl start filebrowser
   ```

7. Verify; get IP and visit the webpage:
   ```bash
   ip addr
   ```

   Go to `http://SERVER_IP:8080`, you can now login as admin:admin.

8. Recovery / reset (if something fails or password is lost)
   
   Stop service, remove DB to force a fresh initial admin creation, then start again:
     ```bash
     sudo systemctl stop filebrowser # Stop the service
     sudo rm -f /var/lib/filebrowser/filebrowser.db # Remove the DB with users
     sudo systemctl start filebrowser # Fire up the service again
     ```
   After restart check the logs for the new initial admin password and repeat user creation. This resets users/settings stored in the DB.

### Set-up permissions

1. Add the filebrowser user to `nasusergroup`.
   ```bash
   sudo usermod -aG nasusergroup filebrowser
   sudo usermod -aG nasguestgroup filebrowser
   ```
   > This allows filebrowser to create and delete files.

2. Create accounts by logging in as admin:admin. Set passwords.