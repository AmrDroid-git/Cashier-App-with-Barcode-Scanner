import subprocess
import time

print("Watching barcode.txt for new scans...\n")

last_seen_lines = 0

while True:
    try:
        # Run ADB command and suppress stderr (2)
        result = subprocess.run(
            ['adb', 'shell', 'cat', '/sdcard/barcode.txt'],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL  # Hides 'No such file' etc.
        )
        lines = result.stdout.decode().splitlines()

        new_lines = lines[last_seen_lines:]
        for line in new_lines:
            if line.strip():
                print("Scanned:", line.strip())

        last_seen_lines = len(lines)

    except Exception:
        pass  # Silently skip any other error

    time.sleep(1)
