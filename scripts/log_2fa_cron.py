#!/usr/bin/env python3

import sys
import os

sys.path.append("/app")

from datetime import datetime, timezone
from totp_utils import generate_totp_code

DATA_FILE = "/data/seed.txt"

def main():
    try:
        # 1. Read seed
        if not os.path.exists(DATA_FILE):
            print("Seed file not found")
            return

        with open(DATA_FILE, "r") as f:
            hex_seed = f.read().strip()

        # 2. Generate TOTP
        code = generate_totp_code(hex_seed)

        # 3. Get current UTC time
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

        # 4. Print formatted result
        print(f"[{now}] 2FA Code: {code}")

    except Exception as e:
        print(f"Cron Error: {e}")

if __name__ == "__main__":
    main()
