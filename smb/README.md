Go back to [Index](./../README.md)

### SMB (Samba)

This file describes how to set up Samba on Ubuntu so NAS folders are accessible from Windows, macOS and Linux over the local network.

The goal of this is to provide SMB feature so users on the network can mount the whole NAS as in this video: https://www.youtube.com/watch?v=brlFVv6NlA8 

Access model in this example:
- guest: read-only
- smbuser (member of sambawrite): authenticated read/write

1. Install Samba
    ```bash
    sudo apt update
    sudo apt install -y samba samba-common-bin
    ```

2. Create group, share directory and base permissions
    ```bash
    # group for writers
    sudo groupadd sambawrite

    # shared dir
    sudo mkdir -p /srv/samba/data
    sudo chown root:sambawrite /srv/samba/data
    sudo chmod 2775 /srv/samba/data   # setgid so new files inherit group
    ```

3. Create an authenticated Samba user (example: smbuser)
    ```bash
    # create normal Linux user
    sudo useradd -m -s /bin/bash smbuser
    sudo passwd smbuser

    # add to writers group
    sudo usermod -aG sambawrite smbuser

    # enable Samba password for the user
    sudo smbpasswd -a smbuser
    ```

4. Minimal smb.conf snippet
- Either use the full `smb.conf` file next to this README file and copy it to target: `cp smb.conf /etc/samba/smb.conf` or:
- Edit /etc/samba/smb.conf and add the following (adjust WORKGROUP and paths as needed):
    ```ini
    [global]
        workgroup = WORKGROUP
        security = user
        map to guest = Bad User
        guest account = nobody

    [data]
        path = /srv/samba/data
        comment = NAS data
        browseable = yes
        read only = yes
        guest ok = yes

        valid users = @sambawrite
        write list = @sambawrite
        force group = sambawrite
        create mask = 0664
        directory mask = 2775
    ```

    For example using nano:
    ```bash
    sudo nano /etc/samba/smb.conf
    ```
- Explanation: guests (wrong/no credentials) are mapped to nobody and get read-only access; members of @sambawrite get write access.

5. Enable and start Samba
    ```bash
    sudo systemctl restart smbd nmbd
    sudo systemctl enable smbd nmbd
    ```

6. Verify access
    ```bash
    # list available shares as guest (no auth)
    smbclient -L //SERVER_IP -N

    # connect as authenticated user
    smbclient //SERVER_IP/data -U smbuser
    ```

7. Notes and recommendations
    >- If you change smb.conf, reload: `sudo systemctl restart smbd`.

### Troubleshooting: "referenced but unset environment variable evaluates to an empty string: smbdoptions"

1) Inspect the systemd unit that failed:
```bash
# show status and recent logs
sudo systemctl status smbd

# show the full unit content (look for EnvironmentFile or $SMBDOPTIONS)
sudo systemctl cat smbd
```

2) Quick safe fix: create the default env file and set the variable to an empty value so the unit can start.
```bash
# create /etc/default/smbd with a safe default
echo 'SMBDOPTIONS=""' | sudo tee /etc/default/smbd >/dev/null

# reload systemd units and restart smbd
sudo systemctl daemon-reload
sudo systemctl restart smbd
sudo systemctl status smbd
```

3) Alternative: if the unit references a different variable name (check output of `systemctl cat smbd`), set that variable instead. Example for lowercase:
```bash
echo 'smbdoptions=""' | sudo tee /etc/default/smbd >/dev/null
sudo systemctl daemon-reload
sudo systemctl restart smbd
```

4) If it still fails, inspect logs for details:
```bash
sudo journalctl -u smbd -n 200 --no-pager
sudo journalctl -u smbd -f   # follow live
```

5) Advanced: remove or change the EnvironmentFile/variable reference in the unit (edit with care):
```bash
# open for inspection/editing (prefer editing an override with systemctl edit)
sudo systemctl edit --full smbd   # advanced; backup before changing
```

Notes
- Setting SMBDOPTIONS to an empty string is a non-destructive quick fix. If you later need extra options, put them into /etc/default/smbd.
- Always use `sudo systemctl daemon-reload` after changing unit files or environment files referenced by units.