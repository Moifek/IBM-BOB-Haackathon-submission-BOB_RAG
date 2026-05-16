"""Parse BOB_USAGE_REPORT.md into dashboard/public/data/bob_sessions.json.

Run after every Bob session to refresh dashboard data:
    uv run python scripts/parse_usage.py
"""
import json
import re
from pathlib import Path

REPO = Path(__file__).parent.parent
REPORT = REPO / "BOB_USAGE_REPORT.md"
OUT = REPO / "dashboard" / "public" / "data" / "bob_sessions.json"

ROW_PATTERN = re.compile(
    r"\|\s*(\d+)\s*\|"          # session id
    r"\s*([^|]*)\|"             # datetime
    r"\s*([^|]+)\|"             # name
    r"\s*([^|]+)\|"             # mode
    r"\s*([^|]*)\|"             # files_read
    r"\s*([^|]*)\|"             # files_written
    r"\s*(\d+|\s*)\s*\|"        # bobcoins
)


def parse() -> list[dict]:
    if not REPORT.exists():
        print(f"⚠️  {REPORT} does not exist yet — writing empty array.")
        return []

    text = REPORT.read_text(encoding="utf-8")
    sessions = []
    for m in ROW_PATTERN.finditer(text):
        try:
            num = int(m.group(1))
            bobcoins_str = m.group(7).strip()
            sessions.append({
                "id": num,
                "datetime": m.group(2).strip(),
                "name": m.group(3).strip(),
                "mode": m.group(4).strip(),
                "files_read": m.group(5).strip(),
                "files_written": m.group(6).strip(),
                "bobcoins": int(bobcoins_str) if bobcoins_str else 0,
            })
        except (ValueError, IndexError):
            continue
    return sessions


def main() -> None:
    sessions = parse()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(sessions, indent=2), encoding="utf-8")
    total = sum(s["bobcoins"] for s in sessions)
    print(f"✅ Wrote {len(sessions)} sessions ({total} Bobcoins total) → {OUT}")


if __name__ == "__main__":
    main()
