"""Start a lesson from the reference checkpoint. Run: python -m tools.catchup NN

Creates branch lessonNN-catchup from tag lessonNN-start of the course template,
and copies your spec/, adr/ and decisions/ folders from your current branch.
Your current branch is not changed.
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

from tools._console import bad, ok, setup_console

ROOT = Path(__file__).resolve().parent.parent
KEEP = ["spec", "adr", "decisions"]


def git(*args: str, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=ROOT, check=check, capture_output=True, text=True, encoding="utf-8")


def main() -> int:
    setup_console()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("lesson", type=int)
    parser.add_argument("--upstream", help="course template URL (default: from .course.json)")
    args = parser.parse_args()

    cfg = json.loads((ROOT / ".course.json").read_text(encoding="utf-8"))
    upstream = args.upstream or cfg.get("upstream")
    tag = f"lesson{args.lesson:02d}-start"
    branch = f"lesson{args.lesson:02d}-catchup"

    if git("status", "--porcelain").stdout.strip():
        bad("יש שינויים שלא נשמרו (commit). לשמור קודם, ואז להריץ שוב.")
        return 1
    current = git("rev-parse", "--abbrev-ref", "HEAD").stdout.strip()
    if upstream:
        fetched = git("fetch", upstream, f"refs/tags/{tag}:refs/tags/{tag}", check=False)
        if fetched.returncode != 0:
            bad(f"לא הצלחתי להביא את {tag} מ־{upstream}: {fetched.stderr.strip()}")
            return 1
    created = git("switch", "-c", branch, tag, check=False)
    if created.returncode != 0:
        bad(f"לא הצלחתי ליצור את הענף {branch}: {created.stderr.strip()}")
        return 1
    for folder in KEEP:
        if git("cat-file", "-e", f"{current}:{folder}", check=False).returncode == 0:
            git("checkout", current, "--", folder)
    git("add", "-A")
    git("commit", "-m", f"catch up to {tag}, keeping my {', '.join(KEEP)}", check=False)
    ok(f"נוצר הענף {branch} מתוך {tag}; התיקיות {', '.join(KEEP)} הועתקו מ־{current}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
