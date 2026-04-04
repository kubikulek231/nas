import datetime
import shutil
import subprocess

from drive_history import append_entry, prune_old_files


HDPARM_BIN = shutil.which("hdparm") or "/usr/sbin/hdparm"

def get_drive_state(device):
    try:
        result = subprocess.run([HDPARM_BIN, "-C", device], capture_output=True, text=True, check=True)
        output = result.stdout
        if 'standby' in output:
            return 0
        elif 'active/idle' in output:
            return 1
        else:
            return None
    except (FileNotFoundError, subprocess.CalledProcessError):
        return None

def main():
    current_time = datetime.datetime.now()
    drive_states = [
        get_drive_state('/dev/disk/by-id/ata-ST4000DM005-2DP166_ZGY1BRJM'),
        get_drive_state('/dev/disk/by-id/ata-ST4000DM005-2DP166_ZGY1BRTB'),
    ]
    entry = {
        "timestamp": current_time.isoformat(),
        "safetank_mirror": max(
            (value for value in drive_states if value in (0, 1)),
            default=None,
        ),
    }

    append_entry(entry, now=current_time)
    prune_old_files(now=current_time)

if __name__ == "__main__":
    main()