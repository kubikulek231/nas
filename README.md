# NAS Setup Scripts and Config

This repository tracks development and a setup of a DIY ODROID H4 NAS 📦.

### Index
1. [Initial Setup](#initial-setup)
2. [ZFS - Filesystem](./zfs/README.md)
3. [Smb](./smb/README.md)
4. [Filebrowser](./filebrowser/README.md)
5. [Jellyfin](./jellyfin/README.md)
6. [Torrent](./torrent/README.md)

> Follow the steps in an organized manner, beginning with 1 ☺️.

### HW
The NAS is using the ODROID H4 board with intel N97 and utilises:
- 2 TB NVME drive for OS and caching torrents,
- Two 4 TB HDD drives for storing stuff,
- 48 GB of RAM for ARC ZFS caching,
- Two more HDD SATA slots waiting for some other beefy HDDs to be plugged. 

### OS
Currently running Ubuntu 24.04.3 LTS (Server).

### Initial Setup

1) Download the latest Ubuntu Server LTS ISO from https://ubuntu.com/download/server.

2) Flash a flashdrive using https://rufus.ie/.

3) Make sure motherboards BIOS is up to date, update if needed and enable in band ECC (very nice feature by Hardkernel - creators of the H4 board).
4) Flash the Ubuntu on the NVME, make sure it is bootable. Add user "nas".
5) Continue ZFS - Filesystem in [Index](#index).