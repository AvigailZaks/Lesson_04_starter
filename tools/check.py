"""Pre-flight check before every push. Run: python -m tools.check

1. Test rule: tests may import only the module(s) this lesson names,
   pytest, the standard library and tests.support.
2. Document structure (spec, decision log) when the lesson requires them.
3. Runs the test suite.
"""
import ast
import json
import re
import subprocess
import sys
from pathlib import Path

from tools._console import bad, info, ok, setup_console
from tools.structure_checks import check_decision_log, check_spec

ROOT = Path(__file__).resolve().parent.parent
RULE = "הבדיקה הזו תלויה במימוש שלך ולא בדרישה. השתמשי רק במודול שהמפגש מציין ובכלים שסופקו."


def load_config() -> dict:
    return json.loads((ROOT / ".course.json").read_text(encoding="utf-8"))


def _allowed(module: str, allowed: list[str]) -> bool:
    top = module.split(".")[0]
    if top in sys.stdlib_module_names or top in ("pytest", "_pytest"):
        return True
    if module == "tests" or module.startswith("tests.support"):
        return True
    return any(module == a or module.startswith(a + ".") for a in allowed)


def scan_tests(cfg: dict) -> list[str]:
    """Return human-readable violations of the test rule."""
    violations: list[str] = []
    allowed = cfg.get("test_imports", [])
    lesson = int(cfg.get("lesson", 0))
    for path in sorted((ROOT / "tests").rglob("*.py")):
        if path.name == "conftest.py" or "support" in path.parts:
            continue
        rel = path.relative_to(ROOT).as_posix()
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=rel)
        except SyntaxError as exc:
            violations.append(f"{rel}:{exc.lineno}: שגיאת תחביר ({exc.msg})")
            continue
        for node in ast.walk(tree):
            names: list[str] = []
            if isinstance(node, ast.Import):
                names = [a.name for a in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
                names = [node.module]
            for name in names:
                if not _allowed(name, allowed):
                    violations.append(f"{rel}:{node.lineno}: import {name} — {RULE}")
            if lesson >= 8 and isinstance(node, ast.Constant) and isinstance(node.value, str):
                if re.match(r"^/[a-z]", node.value):
                    violations.append(f"{rel}:{node.lineno}: כתובת קשיחה '{node.value}' — להשתמש ב־api.call")
    return violations


def main() -> int:
    setup_console()
    cfg = load_config()
    lesson = int(cfg["lesson"])
    print(f"בדיקה לפני push (מפגש {lesson})\n")
    failed = False

    print("1. כלל הבדיקות")
    violations = scan_tests(cfg)
    if violations:
        failed = True
        for v in violations:
            bad(v)
    else:
        ok("הבדיקות מייבאות רק את מה שמותר: " + ", ".join(cfg.get("test_imports", [])))

    if cfg.get("spec"):
        print("\n2. מבנה המפרט (spec/spec.md)")
        for c in check_spec(ROOT / "spec" / "spec.md"):
            (ok if c.ok else bad)(c.message)
            failed |= not c.ok

    if cfg.get("decision_log"):
        print(f"\n3. יומן החלטות (decisions/lesson{lesson:02d}.md)")
        for c in check_decision_log(ROOT / "decisions" / f"lesson{lesson:02d}.md"):
            (ok if c.ok else bad)(c.message)
            failed |= not c.ok

    print("\n4. הרצת הבדיקות")
    result = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider"], cwd=ROOT)
    if result.returncode == 0:
        ok("כל הבדיקות עוברות")
    elif result.returncode == 5:
        bad("לא נמצאו בדיקות")
        failed = True
    else:
        bad("יש בדיקות שנכשלות (ראי למעלה)")
        info("בדיקה שנכשלת כי הקוד עוד לא תוקן — זה בסדר בזמן העבודה; לפני הגשה הכול צריך לעבור.")
        failed = True

    print()
    print("לא מוכן להגשה עדיין." if failed else "מוכן ל־push.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
