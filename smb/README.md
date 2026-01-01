Go back to [Index](./../README.md)

# SMB (Samba) — NAS share setup

Purpose
- Expose ZFS-backed NAS pools over SMB while ensuring the mountpoint directories (`/srv/data/safe` and `/srv/data/fast`) cannot be removed by non-root users.

Prereqs
- Ubuntu with ZFS datasets (example: `safetank/data`, `fasttank/data`).
- Root (sudo) access.

Quick overview
1. Create directories and bind-mounts.
2. Create groups and users.
4. Lock parent directory so only root can create/delete entries.
5. Grant needed rights inside child directories via ACLs, setgid.
6. Verify.

### Create Dirs and Permissions

1) Create hub and mountpoints
    ```bash
    # create hub and subdirs (ensure bind targets exist)
    sudo mkdir -p /srv/data
    sudo mkdir -p /srv/data/safe
    sudo mkdir -p /srv/data/fast

    # example bind mounts for ZFS datasets
    echo '/safetank/data /srv/data/safe none bind 0 0' | sudo tee -a /etc/fstab
    echo '/fasttank/data /srv/data/fast none bind 0 0' | sudo tee -a /etc/fstab
    sudo mount -a
    ```

2) Create groups and users
    ```bash
    # groups
    sudo groupadd nasguestgroup
    sudo groupadd nasusergroup

    # users (example)
    sudo adduser nasuser
    sudo adduser nasguest

    # add users to groups
    sudo usermod -aG nasusergroup nasuser
    sudo usermod -aG nasguestgroup nasguest
    ```

3) Base ownership and classic perms (make parent root-only writable)
This is the primary guard: deleting a directory entry requires write on its parent.
    ```bash
    # ensure parent is root:root and not group-writable
    sudo chown root:root /srv/data
    sudo chmod 0755 /srv/data

    # ensure children exist and are owned by root:nasusergroup
    sudo mkdir -p /srv/data/safe /srv/data/fast
    sudo chown root:nasusergroup /srv/data/safe /srv/data/fast

    # Classic permissions: only owner+group write; others read/execute only
    sudo chmod 2775 /srv/data/safe /srv/data/fast
    # 2 = setgid so group on new files/dirs stays nasusergroup
    ```

    SMB quick setup (concise)
    ```bash
    sudo apt install -y samba samba-common-bin
    sudo smbpasswd -a nasuser
    sudo smbpasswd -a nasguest
    ```
    Example `/etc/samba/smb.conf` share:
    ```ini
    [data]
    path = /srv/data
    browseable = yes
    read only = no
    valid users = @nasguestgroup @nasusergroup
    ```
    > Full file `smb.conf` is available next to this readme.

    Restart Samba:
    ```bash
    sudo systemctl restart smbd nmbd
    ```

### Guest Directory

Guests can write to this dir too, but users can delete what they create. 


2. Setup the dir and permissions:
    ```bash
    # create the directory
    sudo mkdir -p /srv/data/guest

    # make root the owner and nasguestgroup the directory group
    sudo chown root:nasguestgroup /srv/data/guest

    sudo chmod 2775 /srv/data/guest                  # rwx for user/group, r-x for others

    # Add nasuser to guest group
    sudo usermod -aG nasguestgroup nasuser
    sudo usermod -aG nasguestgroup nasguest
    ```