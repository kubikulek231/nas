Go back to [Index](./../README.md)

## SMB (Samba)

This file describes how to set up Samba on Ubuntu so NAS folders are accessible from Windows, macOS, and Linux on the local network.

The goal is to provide SMB access so users on the network can mount the NAS ZFS pools in the usual Windows way (see video): https://www.youtube.com/watch?v=brlFVv6NlA8.

Access model in this example:
- nasguest (member of nasrwgroup): can read and write but not delete
- nasuser (member of nasrwdgroup): authenticated read/write/delete

### Directories and Permissions
---
> We need to create directories that will be used by SMB and Linux users, assign appropriate groups, and set correct file owners. `nasguest` will not have delete rights. `nasuser` will have full read/write/delete rights.

1. Create base dir, which will be shared and served to users and will act as a hub for all the disks.
    ```bash
    # create hub and subdirs (ensure bind targets exist)
    sudo mkdir -p /srv/data
    sudo mkdir -p /srv/data/safe
    sudo mkdir -p /srv/data/fast

    # make the hub owned by root and not writable by group/others
    sudo chown root:root /srv/data
    sudo chmod 0755 /srv/data        # owner: rwx, group/others: r-x — only root can create entries in /srv/data

    # subdirs will be owned and managed by NAS users/groups (see below)
    ```

2. Use bind-mounting to mount safe and fast ZFS storages to `/srv/data` subdirs
    ```bash
    # Run the following commands to append the mounts to /etc/fstab
    echo '/safetank/data /srv/data/safe none bind 0 0' | sudo tee -a /etc/fstab
    echo '/fasttank/data /srv/data/fast none bind 0 0' | sudo tee -a /etc/fstab
    # Do the mounting
    sudo mount -a
    ```

3. Create groups and users, set ownership 
    ```bash
    # groups
    sudo groupadd nasrwdgroup      # full control group (write + delete)
    sudo groupadd nasrwgroup       # limited group

    # users
    sudo adduser nasuser
    sudo adduser nasguest

    # set Linux passwords
    sudo passwd nasuser
    sudo passwd nasguest

    # add users to groups
    sudo usermod -aG nasrwdgroup nasuser
    sudo gpasswd -d nasguest nasrwdgroup || true # ensure nasguest is NOT in nasrwdgroup

    # enable Samba passwords for both users
    sudo smbpasswd -a nasuser
    sudo smbpasswd -a nasguest

    # make nasuser the owner and nasrwdgroup the group for the subdirs only
    sudo chown -R nasuser:nasrwdgroup /srv/data/safe /srv/data/fast

    # group-writable, setgid so new files inherit nasrwdgroup
    sudo chmod -R 2770 /srv/data/safe /srv/data/fast

    # sticky bit so only owners (or root) can delete
    sudo chmod +t /srv/data/safe /srv/data/fast
    ```

### Install and Setup SMB

1. Install Samba
    ```bash
    sudo apt update
    sudo apt install -y samba samba-common-bin
    ```

2. Minimal smb.conf snippet

    Use the full `smb.conf` file next to this README and copy it to the target: `sudo cp smb.conf /etc/samba/smb.conf`.
    
    Or edit in place:
    ```bash
    sudo nano /etc/samba/smb.conf
    ```

3. Enable and start Samba
    ```bash
    sudo systemctl restart smbd nmbd
    sudo systemctl enable smbd nmbd
    ```

4. Verify access
    ```bash
    # list available shares as guest (no auth)
    smbclient -L //SERVER_IP -N

    # connect as authenticated user
    smbclient //SERVER_IP/data -U nasuser
    ```
    In Windows, the share can be mounted as `\\SERVER_IP\data` (see video link above).

5. Notes and recommendations
    > If you change smb.conf, reload: `sudo systemctl restart smbd`.