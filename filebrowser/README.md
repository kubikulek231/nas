Go back to [Index](./../README.md)

### Filebrowser

This file provides guidance on how filebrowser tool for browsing the NAS files using plain browser from given ip address is set up.

Any user within the network can access any files from any device 📱💻 easilly from this place.

### Set-up steps

1. Download and extract filebrowser binary from https://github.com/filebrowser/filebrowser/releases to /opt/filebrowser and place the binary in /usr/local/bin.

     ```bash
     # Go to https://github.com/filebrowser/filebrowser/releases and get exact link by right clicking correct file and copying it.
     # Linux AMD64
     sudo mkdir -p /opt/filebrowser &
     sudo wget <release-url> -O /opt/filebrowser filebrowser.tar.gz &
     sudo tar -xf /opt/filebrowser/filebrowser.tar.gz -C /opt/filebrowser
     sudo mv /opt/filebrowser/filebrowser /usr/local/bin/filebrowser
     sudo chmod +x /usr/local/bin/filebrowser
     ```

2. Create service user and DB dir
   ```bash
   sudo useradd --system --no-create-home --shell /usr/sbin/nologin filebrowser
   sudo mkdir -p /var/lib/filebrowser
   sudo chown -R filebrowser:filebrowser /var/lib/filebrowser
   ```

3. Create systemd service. A file for running the filebrowser as service needs to be created. One can use nano:
   ```bash
   nano /etc/systemd/system/filebrowser.service
   ```
   And copy and save contents of the file available next to this README.

4. Start the daemon
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable --now filebrowser
   ```

5. Find initial admin password (first run)
   - Filebrowser prints the initial admin info to the daemon logs. Check and save it immediately:
     ```bash
     sudo journalctl -u filebrowser -f    # follow logs live
     sudo journalctl -u filebrowser --no-pager | tail -n 200 | grep -i admin
     ```
   - Save the password in a secure place (password manager or encrypted note).

6. Create users
   - Recommended: use the web UI (http://SERVER_IP:8080) to set precise permissions:
     - admin: full access (or admin role)
     - guest: scope = / (or mount), enable read + write (create/upload/rename), disable delete
   - Users can be created using CLI as well (NOT RECOMMENDED):
      ```bash
      sudo -u filebrowser /usr/local/bin/filebrowser users list
      sudo -u filebrowser /usr/local/bin/filebrowser users add admin 'StrongAdminPass'
      sudo -u filebrowser /usr/local/bin/filebrowser users add guest 'GuestPass'
      ```

7. Verify
   ```bash
   sudo -u filebrowser /usr/local/bin/filebrowser users list
   sudo -u filebrowser ls -la /mnt/data1   # or your mountpoint
   ```

8. Recovery / reset (if something fails or password is lost)
   - Stop service, remove DB to force a fresh initial admin creation, then start again:
     ```bash
     sudo systemctl stop filebrowser # Stop the service
     sudo rm -f /var/lib/filebrowser/filebrowser.db # Remove the DB with users
     sudo systemctl start filebrowser # Fire up the service again
     ```
   - After restart check the logs for the new initial admin password and repeat user creation. This resets users/settings stored in the DB.

>Notes
>- Use web UI for fine-grained permission toggles; POSIX ACLs/groups manage filesystem-level access and do not substitute filebrowser's per-user delete/create controls.
>- Keep the DB path documented and backed up if you want persistent user data.