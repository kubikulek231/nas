import subprocess
import json
import os
import datetime

def get_drive_state(device):
    try:
        result = subprocess.run(['sudo', 'hdparm', '-C', device], capture_output=True, text=True, check=True)
        output = result.stdout
        if 'standby' in output:
            return 0
        elif 'active/idle' in output:
            return 1
        else:
            return None
    except subprocess.CalledProcessError:
        return None

def main():
    current_time = datetime.datetime.now()
    month_file = current_time.strftime("%Y-%m.json")
    data_dir = os.path.dirname(__file__)
    data_file = os.path.join(data_dir, month_file)

    # Load existing data
    if os.path.exists(data_file):
        with open(data_file, 'r') as f:
            data = json.load(f)
    else:
        data = []

    # Append new entry
    entry = {
        "timestamp": current_time.isoformat(),
        "sda": get_drive_state('/dev/disk/by-id/ata-ST4000DM005-2DP166_ZGY1BRJM'),
        "sdb": get_drive_state('/dev/disk/by-id/ata-ST4000DM005-2DP166_ZGY1BRTB')
    }
    data.append(entry)

    # Save data
    with open(data_file, 'w') as f:
        json.dump(data, f, indent=2)

    # Clean old files (older than 2 months)
    now = datetime.datetime.now()
    two_months_ago = now - datetime.timedelta(days=60)
    for file in os.listdir(data_dir):
        if file.endswith('.json') and file != month_file:
            try:
                year, month = map(int, file[:-5].split('-'))
                file_date = datetime.datetime(year, month, 1)
                if file_date < two_months_ago:
                    os.remove(os.path.join(data_dir, file))
            except ValueError:
                pass

if __name__ == "__main__":
    main()