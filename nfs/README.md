Go back to [Index](./../README.md)

## NFS

This file describes how to set up NFS on Ubuntu so NAS folders are accessible from Linux and macOS on the local network. NFS can also be used from Windows (Client for NFS) but behavior and authentication differ.

Goal: provide NFS access so users on the network can mount the NAS ZFS pools similarly to the SMB setup.

Access model in this example:
- nasguest (member of nasrwgroup): can write files as the guest account (mapped) but should not be able to delete other users' files (sticky bit + ownership).
- nasuser (member of nasrwdgroup): authenticated full read/write/delete when UIDs/GIDs match on clients (or when using Kerberos).

Important note about NFS auth:
- NFS uses UID/GID to determine file permissions. For per-user permissions to work across machines you must ensure consistent UIDs/GIDs on clients or use NFSv4 with idmapping or Kerberos (sec=krb5). If you cannot ensure consistent UIDs, use guest mapping (all_squash + anonuid/anongid) for the guest share.

### Directories and Permissions (same as SMB)
---
Follow the same directory layout as the SMB guide. Example commands:

1. Create base dir and subdirs
    ```bash
    # create hub and subdirs (ensure bind targets exist)
    sudo mkdir -p /srv/data
    sudo mkdir -p /srv/data/safe
    sudo mkdir -p /srv/data/fast

    # make the hub owned by root and not writable by group/others
    sudo chown root:root /srv/data
    sudo chmod 0755 /srv/data

    # subdirs will be owned and managed by NAS users/groups (see below)
    ```

2. Bind-mount ZFS datasets (if applicable)
    ```bash
    echo '/safetank/data /srv/data/safe none bind 0 0' | sudo tee -a /etc/fstab
    echo '/fasttank/data /srv/data/fast none bind 0 0' | sudo tee -a /etc/fstab
    sudo mount -a
    ```

3. Create groups and users and set ownership (reuse same users/groups as SMB)
    ```bash
    sudo groupadd nasrwdgroup      # full control group (write + delete)
    sudo groupadd nasrwgroup       # limited group

    sudo adduser nasuser
    sudo adduser nasguest

    sudo passwd nasuser
    sudo passwd nasguest

    sudo usermod -aG nasrwdgroup nasuser
    sudo gpasswd -d nasguest nasrwdgroup || true

    # make nasuser the owner and nasrwdgroup the group for the subdirs
    sudo chown -R nasuser:nasrwdgroup /srv/data/safe /srv/data/fast

    # group-writable, setgid so new files inherit nasrwdgroup
    sudo chmod -R 2770 /srv/data/safe /srv/data/fast

    # sticky bit so only file owners (or root) can delete
    sudo chmod +t /srv/data/safe /srv/data/fast
    ```

### Install and configure NFS server

1. Install NFS server
    ```bash
    sudo apt update
    sudo apt install -y nfs-kernel-server
    ```

2. Decide on export strategy
- If you want unauthenticated guest access for the "safe" area (so clients don't need local nasguest accounts), map all access to the nasguest account with all_squash + anonuid/anongid.
- If you want per-user permissions for the "fast" area, ensure clients have matching UIDs/GIDs for nasuser or use Kerberos-based authentication.

3. Find UID/GID to use for anon mapping
    ```bash
    id -u nasguest   # anonuid
    getent group nasrwgroup | cut -d: -f3   # anongid (or use nasrwdgroup as needed)
    ```

4. Add exports to /etc/exports
    Example entries (replace 192.168.1.0/24 with your network, and replace anonuid/anongid with the numbers from the previous step):

    - safe: guest-mapped share (clients get nasguest)
      /srv/data/safe  192.168.1.0/24(rw,sync,no_subtree_check,all_squash,anonuid=1001,anongid=1001)

    - fast: requires client UIDs to match nasuser for proper owner-based delete privileges
      /srv/data/fast  192.168.1.0/24(rw,sync,no_subtree_check,root_squash)

    To append these lines:
    ```bash
    # example; replace anonuid/anongid with actual numeric IDs
    echo '/srv/data/safe  192.168.1.0/24(rw,sync,no_subtree_check,all_squash,anonuid=1001,anongid=1001)' | sudo tee -a /etc/exports
    echo '/srv/data/fast  192.168.1.0/24(rw,sync,no_subtree_check,root_squash)' | sudo tee -a /etc/exports
    ```

5. Apply exports and start NFS
    ```bash
    sudo exportfs -ra
    sudo systemctl restart nfs-kernel-server
    sudo systemctl enable nfs-kernel-server
    ```

### Verify and mount from clients

- From another Linux machine:
    ```bash
    # list exported shares
    showmount -e SERVER_IP

    # mount (example)
    sudo mount -t nfs SERVER_IP:/srv/data /mnt/data -o vers=4
    # or mount specific subdir:
    sudo mount -t nfs SERVER_IP:/srv/data/safe /mnt/safe -o vers=4
    ```

- From macOS:
    ```bash
    sudo mount -t nfs SERVER_IP:/srv/data/safe /Volumes/safe
    # Or use Finder -> Go -> Connect to Server -> nfs://SERVER_IP/srv/data/safe
    ```

- From Windows (Client for NFS required; behavior differs and UID mapping required):
    - Windows NFS support is limited; if needed, enable "Services for NFS" and ensure UID/GID mapping or use SMB instead for Windows clients.

### Notes, limitations and recommendations
- NFS enforces permissions by UID/GID. For predictable per-user behavior across clients, ensure consistent UIDs/GIDs on all machines, or use NFSv4 idmapd or Kerberos (sec=krb5) for proper authentication.
- The "safe" export above maps all remote operations to a single local account (nasguest) so clients do not need local accounts. This is good for simple guest access but loses per-user auditing and true per-user permissions.
- The sticky bit on directories prevents deletion of files by users who don't own them; combined with ownership and setgid it approximates the SMB behavior described earlier.
- If you need strong, per-user authentication from heterogeneous clients (Linux, macOS, Windows), consider exporting via SMB (Samba) or combining NFS with LDAP and Kerberos.

If you want, I can:
- produce the exact /etc/exports lines with your local network and numeric UID/GID filled in, or
- add example systemd automount entries for clients.
