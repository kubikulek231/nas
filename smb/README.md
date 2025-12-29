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