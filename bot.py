from pathlib import Path
from datetime import datetime
import os
import requests

BOT_TOKEN = os.environ["BOT_TOKEN"]
ALLOWED_USER_ID = str(os.environ["ALLOWED_USER_ID"])

BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

notes_dir = Path("notes")
data_dir = Path("data")

notes_dir.mkdir(exist_ok=True)
data_dir.mkdir(exist_ok=True)

offset_file = data_dir / "offset.txt"

if offset_file.exists():
    offset = int(offset_file.read_text().strip() or "0")
else:
    offset = 0

r = requests.get(
    f"{BASE_URL}/getUpdates",
    params={"offset": offset + 1, "timeout": 0},
    timeout=30
)

updates = r.json().get("result", [])

latest_offset = offset

for update in updates:
    latest_offset = max(latest_offset, update["update_id"])

    message = update.get("message")
    if not message:
        continue

    user_id = str(message["from"]["id"])

    if user_id != ALLOWED_USER_ID:
        continue

    text = message.get("text", "").strip()

    if not text:
        continue

    now = datetime.now()

    filename = notes_dir / f"{now:%Y-%m-%d}.md"

    block = f"\n## {now:%H:%M}\n\n{text}\n"

    if filename.exists():
        with open(filename, "a", encoding="utf-8") as f:
            f.write(block)
    else:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"# Notes {now:%Y-%m-%d}\n")
            f.write(block)

offset_file.write_text(str(latest_offset))
