from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import os
import requests
import json

BOT_TOKEN = os.environ["BOT_TOKEN"]
ALLOWED_USER_ID = str(os.environ["ALLOWED_USER_ID"])

BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

notes_dir = Path("notes")
data_dir = Path("data")

notes_dir.mkdir(exist_ok=True)
data_dir.mkdir(exist_ok=True)

offset_file = data_dir / "offset.txt"
heartbeat_file = data_dir / "last_run.txt"
debug_file = data_dir / "debug.log"

IST = ZoneInfo("Asia/Kolkata")

if offset_file.exists():
    offset = int(offset_file.read_text().strip() or "0")
else:
    offset = 0

now = datetime.now(IST)

heartbeat_file.write_text(
    f"Last Run: {now:%Y-%m-%d %H:%M:%S IST}\n"
)

try:
    r = requests.get(
        f"{BASE_URL}/getUpdates",
        params={
            "offset": offset + 1,
            "timeout": 0
        },
        timeout=30
    )

    data = r.json()

    with open(debug_file, "a", encoding="utf-8") as f:
        f.write("\n")
        f.write("=" * 50 + "\n")
        f.write(f"RUN: {now:%Y-%m-%d %H:%M:%S IST}\n")
        f.write(json.dumps(data, indent=2))
        f.write("\n")

except Exception as e:
    with open(debug_file, "a", encoding="utf-8") as f:
        f.write(f"\nERROR: {e}\n")
    raise

updates = data.get("result", [])

print("Telegram Response:")
print(data)

print("Updates Found:", len(updates))

latest_offset = offset
saved_count = 0

for update in updates:
    latest_offset = max(
        latest_offset,
        update["update_id"]
    )

    print(
        "Processing Update:",
        update["update_id"]
    )

    message = update.get("message")

    if not message:
        continue

    user_id = str(
        message["from"]["id"]
    )

    if user_id != ALLOWED_USER_ID:
        continue

    text = (
        message.get("text", "")
        .strip()
    )

    if not text:
        continue

    if text.startswith("/"):
        print(
            "Skipping command:",
            text
        )
        continue

    now = datetime.now(IST)

    filename = (
        notes_dir /
        f"{now:%Y-%m-%d}.md"
    )

    block = (
        f"\n## {now:%H:%M}\n\n"
        f"{text}\n"
    )

    if filename.exists():
        with open(
            filename,
            "a",
            encoding="utf-8"
        ) as f:
            f.write(block)
    else:
        with open(
            filename,
            "w",
            encoding="utf-8"
        ) as f:
            f.write(
                f"# Notes {now:%Y-%m-%d}\n"
            )
            f.write(block)

    saved_count += 1

    print("Saved:", text)

offset_file.write_text(
    str(latest_offset)
)

heartbeat_file.write_text(
    f"Last Run: {datetime.now(IST):%Y-%m-%d %H:%M:%S IST}\n"
    f"Updates Found: {len(updates)}\n"
    f"Messages Saved: {saved_count}\n"
    f"Offset: {latest_offset}\n"
)

print("Messages Saved:", saved_count)
print("Latest Offset:", latest_offset)
