Go back to [Index](./../README.md)

## SMB (Samba)

This file describes how to set up Samba on Ubuntu so NAS folders are accessible from Windows, macOS, and Linux on the local network.

The goal is to provide SMB access so users on the network can mount the NAS ZFS pools in the usual Windows way (see video): https://www.youtube.com/watch?v=brlFVv6NlA8.

Access model in this example:

Users, who can only create, modify or delete their OWN created files:
- nasguest (member of nasusergroup)
- custom users userX, userY...

Admins, who can edit or delete others files too:
- nasadmin (member of nasadmingroup) 

### Directories, Users and Permissions
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

3. Create groups and users
    ```bash
    # groups
    sudo groupadd nasadmingroup    # admin group (full control on subdirs)
    sudo groupadd nasusergroup     # regular users (can create files, only owner can edit/delete)

    # users
    sudo adduser nasadmin
    sudo adduser nasguest

    # set Linux passwords
    sudo passwd nasadmin
    sudo passwd nasguest
    ```

4. Add Users to Groups
    ```bash
    # group membership
    # nasguest should be in nasusergroup so it can create files as a regular user
    sudo usermod -aG nasusergroup nasguest
    # nasadmin is an admin; add to nasadmingroup so it has admin rights
    sudo usermod -aG nasadmingroup nasadmin
5. Set base Linux File Permissions
    ```bash
    # Ensure /srv/data is root-owned and not writable
    sudo chown root:root /srv/data
    sudo chmod 0755 /srv/data

    # Make subdirs owned by the admin user (nasadmin) with group nasadmingroup so admins have full control.
    sudo mkdir -p /srv/data/safe /srv/data/fast
    # Make root the directory owner and keep nasadmingroup as the group.
    # This ensures only root (or the file owner) can remove the subdir entries when the sticky bit is set.
    sudo chown root:nasadmingroup /srv/data/safe /srv/data/fast

    # setgid so new files/dirs inherit nasadmingroup; base perms block others
    sudo chmod 2770 /srv/data/safe /srv/data/fast

    # sticky bit so only file owners (or directory owner nasadmin, or root) can delete files; admins can manage via group ACLs
    sudo chmod +t /srv/data/safe /srv/data/fast
    ```
6. Install ACL
    ```bash
    # Install ACL utility so setfacl/getfacl are available
    sudo apt update
    sudo apt install -y acl
    ```
7. Set ACL Permissions (fine-grained access)
    ```bash
    # If using ZFS, enable POSIX ACL support on the datasets backing the bind mounts
    # (replace dataset names if different)
    sudo zfs set acltype=posixacl safetank/data
    sudo zfs set aclmode=passthrough safetank/data
    sudo zfs set xattr=sa safetank/data

    sudo zfs set acltype=posixacl fasttank/data
    sudo zfs set aclmode=passthrough fasttank/data
    sudo zfs set xattr=sa fasttank/data

    # Apply ACLs:
    # - grant nasadmingroup rwx on files/directories (admins full control)
    # - grant nasusergroup rwx on the directories so regular users can create entries
    # - default ACL: owner::rwx, group::rwx (group == nasadmingroup), others none
    sudo setfacl -R -m g:nasadmingroup:rwx /srv/data/safe /srv/data/fast
    sudo setfacl -R -m g:nasusergroup:rwx /srv/data/safe /srv/data/fast
    sudo setfacl -R -m u::rwx,g::rwx,o::--- /srv/data/safe /srv/data/fast

    # Default (inherited) ACLs so new files:
    # - owner (creator) gets rwx on their files
    # - nasadmingroup gets rwx on all new files (admin full access)
    # - nasusergroup receives directory-level rights but does not get group-write on individual files
    sudo setfacl -R -d -m u::rwx,g::rwx,o::--- /srv/data/safe /srv/data/fast
    # ensure nasusergroup can create entries in directories (inherit)
    sudo setfacl -R -d -m g:nasusergroup:rwx /srv/data/safe /srv/data/fast
    ```

### Install and Setup SMB

1. Install Samba
    ```bash
    sudo apt update
    sudo apt install -y samba samba-common-bin
    ```
2. Setup SMB passwords
    ```bash
    # enable Samba passwords for both users
    sudo smbpasswd -a nasadmin
    sudo smbpasswd -a nasguest
    ```
3. Minimal smb.conf snippet

    Use the full `smb.conf` file next to this README and copy it to the target: `sudo cp smb.conf /etc/samba/smb.conf`.
    
    Or edit in place:
    ```bash
    sudo nano /etc/samba/smb.conf
    ```

    Note: allow new users in the share with "valid users"
    You must permit new Samba users to access the share via smb.conf. Example share entry:
    ```ini
    # /etc/samba/smb.conf (excerpt)
    [data]
      path = /srv/data
      browseable = yes
      read only = no
      # allow specific users (space-separated or comma-separated)
      # valid users = nasguest userX
      # or allow whole groups:
      valid users = @nasadmingroup @nasusergroup
    ```
    
    After editing, reload Samba:
    ```bash
    sudo systemctl restart smbd nmbd
    testparm -s /etc/samba/smb.conf
    ```

4. Enable and start Samba
    ```bash
    sudo systemctl restart smbd nmbd
    sudo systemctl enable smbd nmbd
    ```

5. Verify access
    ```bash
    # list available shares as guest (no auth)
    smbclient -L //SERVER_IP -N

    # connect as authenticated user
    smbclient //SERVER_IP/data -U nasguest
    ```
    In Windows, the share can be mounted as `\\SERVER_IP\data` (see video link above).

6. Notes and recommendations
    > If you change smb.conf, reload: `sudo systemctl restart smbd`.

### Multi-user: apply shared-directory behaviour to subdirs (keep /srv/data non-writable)

This workflow is integrated above in "Directories and Permissions" — see the ownership, setgid, sticky bit, and setfacl commands in step 3 which apply the shared-directory policy to /srv/data/safe and /srv/data/fast. Do not make /srv/data itself writable; apply write permissions only to the chosen subdirectories.

Samba notes
- No special smb.conf is required beyond exposing the filesystem path. Samba will enforce the filesystem permissions. If you expose the shared dir, users will see only what their UNIX permissions allow.
- If you want users to connect as their Windows accounts, ensure UID mapping or join AD so UNIX UID/GID consistency is maintained.

### Adding a new user (example)
```bash
# create the Linux account and add it to the regular users group so it can create files
sudo adduser userX
sudo usermod -aG nasusergroup userX

# enable Samba access and set password for the user
sudo smbpasswd -a userX
```

Remove user by:

```bash
userdel -r userX
```

Notes:
- Members of nasusergroup can create files in the configured subdirs; created files are owned by the creator and, due to default ACLs, the creator has full rights on their files.
- Members of nasadmingroup have rwx on all files in the subdirs (admin full control).
- The sticky bit plus ownership prevents regular users from deleting or editing others' files; admins can manage files via their nasadmingroup permissions.

```bash
# OPTIONAL: create a per-user directory (if you want per-user private area)
sudo mkdir -p /srv/data/fast/users/userX
sudo chown userX:nasusergroup /srv/data/fast/users/userX
sudo chmod 750 /srv/data/fast/users/userX
sudo setfacl -R -m u::rwx,g::r-x,o::--- /srv/data/fast/users/userX
sudo setfacl -R -d -m u::rwx,g::r-x,o::--- /srv/data/fast/users/userX
```