Go back to [Index](./../README.md)

## NFS

This file describes how to set up NFS on Ubuntu using the same users/groups created for SMB so NAS folders are accessible from Linux and macOS on the local network.

Summary of expected local accounts (created during SMB setup)
- Admins: nasadmin (member of nasadmingroup)
- Regular users: nasguest and other members of nasusergroup
- Top-level layout: /srv/data (root-owned), writable subdirs: /srv/data/safe and /srv/data/fast

1) Install NFS server
    ```bash
    sudo apt update
    sudo apt install -y nfs-kernel-server
    ```
2) Edit `/etc/exports` entries (replace NETWORK with your network, e.g. 192.168.1.0/24):

    ```bash
    # per-user, UID/GID enforced, root squashed
    /srv/data/safe    192.168.1.0/24(rw,sync,no_subtree_check,root_squash)
    /srv/data/fast    192.168.1.0/24(rw,sync,no_subtree_check,root_squash)
    /srv/data    192.168.1.0/24(rw,sync,no_subtree_check,root_squash)
    ```

    You can do it by for example running these commands:
    ```bash
    echo "/srv/data/safe    192.168.1.0/24(rw,sync,no_subtree_check,root_squash)" | sudo tee -a /etc/exports
    echo "/srv/data/fast    192.168.1.0/24(rw,sync,no_subtree_check,root_squash)" | sudo tee -a /etc/exports
    echo "/srv/data    192.168.1.0/24(rw,sync,no_subtree_check,root_squash)" | sudo tee -a /etc/exports
    ```

3) Apply exports
    ```bash
    sudo exportfs -ra
    sudo systemctl restart nfs-kernel-server
    sudo systemctl enable nfs-kernel-server
    ```

4) Client mount examples

Linux client:
```bash
# list exports
showmount -e SERVER_IP

# mount safe (guest-mapped)
sudo mount -t nfs SERVER_IP:/srv/data/safe /mnt/safe -o vers=4

# mount fast (per-user; ensure UID/GID match on client)
sudo mount -t nfs SERVER_IP:/srv/data/fast /mnt/fast -o vers=4
```

Windows Client (run in administartor powershell):
```pwsh
# Enable the Windows NFS features
Enable-WindowsOptionalFeature -Online -FeatureName `
  ServicesForNFS-ClientOnly, `
  ClientForNFS-Infrastructure, `
  NFS-Administration `
  -All
```
> You can use `enable-nfs-client.ps1` script file next to this readme.

Open CMD (Not as administrator). To mount a drive to Y:

```cmd
mount SERVER_IP:/srv/data y:
```

To unmount:
```cmd
umount Y:
```

>On Windows, the UID (User ID) and GID (Group ID) under which the client is accessing the NFS server needs to be set if one does not want to use defaults. 
>
>You can use `set-nfs-uid-gid.ps1` script file next to this readme.
>
>For getting UID run `getent passwd $(seq 1000 2000)` on NAS.
>
>For getting GID run `getent group`.