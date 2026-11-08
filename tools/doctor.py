"""Environment check. Run: python -m tools.doctor

Checks Python 3.12, an active virtual environment, pinned packages,
UTF-8 mode, the SQLite version (STRICT tables need 3.37+) and time zone data.
"""
import importlib.metadata as md
import re
import sqlite3
import sys
from pathlib import Path

from tools._console import bad, info, ok, setup_console

ROOT = Path(__file__).resolve().parent.parent
MIN_SQLITE = (3, 37, 0)


def _pins(path: Path, seen: set) -> list[tuple[str, str]]:
    """Read name==version pins from a requirements file, following -r includes."""
    pins: list[tuple[str, str]] = []
    if path in seen or not path.exists():
        return pins
    seen.add(path)
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        if line.startswith("-r "):
            pins += _pins(path.parent / line[3:].strip(), seen)
            continue
        req, _, marker = line.partition(";")
        marker = marker.strip()
        if "win32" in marker and sys.platform != "win32":
            continue
        m = re.match(r"^([A-Za-z0-9_.\-]+)==([^\s]+)$", req.strip())
        if m:
            pins.append((m.group(1), m.group(2)))
    return pins


def check_python() -> bool:
    v = sys.version_info
    if (v.major, v.minor) == (3, 12):
        ok(f"Python {v.major}.{v.minor}.{v.micro}")
        return True
    bad(f"Python {v.major}.{v.minor} — הקורס דורש 3.12")
    info("תיקון: למחוק את .venv וליצור מחדש:  py -3.12 -m venv .venv")
    return False


def check_venv() -> bool:
    if sys.prefix != sys.base_prefix:
        ok(f"סביבה וירטואלית: {sys.prefix}")
        return True
    bad("לא רצה מתוך סביבה וירטואלית")
    info("תיקון: להריץ כך:  .venv\\Scripts\\python -m tools.doctor")
    return False


def check_packages() -> bool:
    good = True
    for name, version in _pins(ROOT / "requirements-dev.txt", set()):
        try:
            installed = md.version(name)
        except md.PackageNotFoundError:
            bad(f"החבילה {name} לא מותקנת")
            good = False
            continue
        if installed != version:
            bad(f"{name} {installed} מותקנת, נדרשת {version}")
            good = False
    if good:
        ok("כל החבילות מותקנות בגרסאות הנכונות")
    else:
        info("תיקון:  .venv\\Scripts\\python -m pip install -r requirements-dev.txt")
    return good


def check_utf8() -> bool:
    enc = (sys.stdout.encoding or "").lower().replace("-", "")
    if sys.flags.utf8_mode or enc == "utf8":
        ok("קידוד UTF-8")
        return True
    bad(f"המסוף לא במצב UTF-8 (כרגע: {sys.stdout.encoding}); עברית עלולה להישבר")
    info('תיקון (פעם אחת):  [Environment]::SetEnvironmentVariable("PYTHONUTF8", "1", "User")')
    info("ואז לסגור ולפתוח מחדש את המסוף ואת VS Code.")
    return False


def check_sqlite() -> bool:
    version = tuple(int(p) for p in sqlite3.sqlite_version.split(".")[:3])
    if version >= MIN_SQLITE:
        ok(f"SQLite {sqlite3.sqlite_version}")
        return True
    bad(f"SQLite {sqlite3.sqlite_version} ישן מדי (נדרש 3.37 ומעלה עד מפגש 9)")
    info("לא חוסם עכשיו. לדווח לטכנאי המעבדה: נדרשת התקנה עדכנית של Python 3.12.")
    return True  # not blocking before lesson 9


def check_timezones() -> bool:
    try:
        from zoneinfo import ZoneInfo

        ZoneInfo("Asia/Jerusalem")
    except Exception as exc:  # noqa: BLE001 - report any failure to the student
        bad(f"נתוני אזורי זמן חסרים ({exc.__class__.__name__})")
        info("תיקון:  .venv\\Scripts\\python -m pip install -r requirements-dev.txt  (החבילה tzdata)")
        return False
    ok("אזורי זמן (Asia/Jerusalem)")
    return True


def main() -> int:
    setup_console()
    print("בדיקת סביבה (tools.doctor)\n")
    results = [check_python(), check_venv(), check_packages(), check_utf8(), check_sqlite(), check_timezones()]
    print()
    if all(results):
        print("הכול תקין. השלב הבא:  .venv\\Scripts\\python -m pytest")
        return 0
    print("יש מה לתקן (ראי למעלה). אחרי התיקון, להריץ שוב את doctor.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
