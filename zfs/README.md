# ZFS (disks)

Go back to [Index](./../README.md)

This document shows how to create and tune two ZFS pools used on this NAS:
- Safe (mirrored) pool: safetank with dataset /safetank/data
- Fast (NVMe) pool: fasttank with dataset /fasttank/data

1. Find stable disk IDs — Run this once to see the persistent names for your disks:
```bash
ls -l /dev/disk/by-id
```

1. Create mirrored safe pool ("safetank") — replace devices with your actual block devices:
```bash
# Example – adjust to your IDs
sudo zpool create safetank \
  mirror \
  /dev/disk/by-id/ata-WDC_WD40EFRX-68WT0N0_WD-WCC4E1234567 \
  /dev/disk/by-id/ata-WDC_WD40EFRX-68WT0N0_WD-WCC4E1234568

sudo zfs create safetank/data
```

2. Create fast pool ("fasttank") on an LVM logical volume (example)
```bash
# create LV (adjust vg name and size as needed)
sudo lvcreate -l 100%FREE -n fastdata-lv ubuntu-vg

# create ZFS pool on the LV and dataset
sudo zpool create fasttank /dev/ubuntu-vg/fastdata-lv
sudo zfs create fasttank/data
```

3. Common ZFS tuning (apply to both pools/datasets)
```bash
# disable atime and enable lz4 compression
sudo zfs set atime=off safetank
sudo zfs set compression=lz4 safetank
sudo zfs set atime=off safetank/data
sudo zfs set compression=lz4 safetank/data

sudo zfs set atime=off fasttank
sudo zfs set compression=lz4 fasttank
sudo zfs set atime=off fasttank/data
sudo zfs set compression=lz4 fasttank/data
```

4. ARC tuning (example: 4GB min, 40GB max on a 48GB system)
```bash
echo "options zfs zfs_arc_min=4294967296" | sudo tee /etc/modprobe.d/zfs-arc.conf
echo "options zfs zfs_arc_max=42949672960" | sudo tee -a /etc/modprobe.d/zfs-arc.conf
sudo update-initramfs -u
sudo reboot
```

5. Snapshots with Sanoid
```bash
sudo apt update
sudo apt install -y sanoid
# place sanoid.conf in /etc/sanoid/sanoid.conf (example config next to this README)
sudo systemctl enable --now sanoid.timer
```

6. Verify pools, datasets and snapshots
```bash
# list pools and datasets
sudo zpool status
sudo zfs list

# verify datasets
sudo zfs list safetank safetank/data fasttank fasttank/data

# trigger and list snapshots (sanoid)
sudo sanoid --debug --take-snapshots
sudo sanoid --debug --prune-snapshots
zfs list -t snapshot
```

7. Set HDD power management

```bash
# Again list the disks by ID, use the ids to set the values for testing
sudo hdparm -B 254 -S 240 \
  /dev/disk/by-id/ata-ST4000DM005-2DP166_ZGY1BRJM \
  /dev/disk/by-id/ata-ST4000DM005-2DP166_ZGY1BRTB
# -B 254 sets APM mode to 254
# -S 240 is time before spindown (20 minutes)

# To make this persistent, edit /etc/hdparm.conf with:
/dev/disk/by-id/ata-ST4000DM005-2DP166_ZGY1BRJM {
    apm = 254
    spindown_time = 240
}

/dev/disk/by-id/ata-ST4000DM005-2DP166_ZGY1BRTB {
    apm = 254
    spindown_time = 240
}
```

8. Enable power saving
```bash
# Install powertop
sudo apt install powertop

# To make this persistent, create systemd service /etc/systemd/system/powertop.service with:
[Unit]
Description=Powertop tunings

[Service]
Type=oneshot
ExecStart=/usr/sbin/powertop --auto-tune

[Install]
WantedBy=multi-user.target

# Start it using
sudo systemctl daemon-reload
sudo systemctl enable --now powertop.service
```

9. Save CPU power by clocking down
```bash
# Create a slim systemd service:
sudo nano /etc/systemd/system/cpupower-governor.service

# Put:
[Unit]
Description=Set CPU governor to powersave

[Service]
Type=oneshot
ExecStart=/usr/bin/cpupower frequency-set -g powersave

[Install]
WantedBy=multi-user.target

# Enable
sudo systemctl daemon-reload
sudo systemctl enable --now cpupower-governor.service
```
