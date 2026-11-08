"""Structure checks for student documents (spec, decision log).

Used by tools.check (students) and by the grader, so both give the same answer.
Headings and identifiers are English; content may be Hebrew.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

SPEC_HEADINGS = [
    "Problem",
    "Stakeholders and Actors",
    "Scope",
    "Out of Scope",
    "Functional Requirements",
    "Non-Functional Requirements",
    "Constraints",
    "Assumptions and Open Questions",
    "User Flows",
    "Acceptance Criteria",
    "Context Diagram",
]

DECISION_FIELDS = ["Decision", "Options", "AI proposed", "Chosen and why", "Risk", "Covered by test"]

_HEADING = re.compile(r"^\s{0,3}(#{1,4})\s+(.+?)\s*#*\s*$")
_UNIT = re.compile(
    r"(ms\b|millisecond|\bsec|second|minute|hour|\bdays?\b|%|percent|\b[kmg]b\b|byte|\busers?\b|"
    r"request|\bp\d{2}\b|\brps\b|items?\b|files?\b|cases?\b|errors?\b|failures?\b|"
    r"שני|מילישני|דק|שע|ימים|יום|משתמש|בקש|אחוז|בתים|מגה|פריט|קבצ|קובץ|גיש|מקר|שגיא|כשל)",
    re.IGNORECASE,
)
_STAKEHOLDER_GROUPS = {
    "לקוחה (client)": ["client", "לקוח"],
    "צלמת ראשית (lead provider)": ["lead", "ראשי"],
    "ספקים נוספים (other providers)": [
        "participant", "second photographer", "videographer", "other provider",
        "נוספ", "וידאו", "משתתפ", "משתתף",
    ],
    "מבקרת אנונימית (anonymous visitor)": ["anonymous", "visitor", "אנונימ", "מבקר", "אורח"],
}


@dataclass
class Check:
    name: str
    ok: bool
    message: str


def sections(markdown: str) -> list[tuple[str, str]]:
    """Return (heading, body) pairs in document order."""
    result: list[tuple[str, list[str]]] = []
    for line in markdown.splitlines():
        m = _HEADING.match(line)
        if m:
            result.append((m.group(2).strip(), []))
        elif result:
            result[-1][1].append(line)
    return [(h, "\n".join(body).strip()) for h, body in result]


def _section(secs: list[tuple[str, str]], name: str) -> str:
    for heading, body in secs:
        if heading.lower() == name.lower():
            return body
    return ""


def _ids(text: str, prefix: str) -> list[str]:
    seen: list[str] = []
    for m in re.finditer(rf"\b{prefix}-(\d+)\b", text):
        ident = f"{prefix}-{int(m.group(1))}"
        if ident not in seen:
            seen.append(ident)
    return seen


def _chunks(text: str, prefix: str) -> dict[str, str]:
    """Split text into chunks that start at each definition of PREFIX-n."""
    chunks: dict[str, str] = {}
    matches = list(re.finditer(rf"(?m)^[\s>*\-\d.|#]*\**{prefix}-(\d+)\b", text))
    for i, m in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        ident = f"{prefix}-{int(m.group(1))}"
        chunks.setdefault(ident, text[m.start():end])
    return chunks


def ac_ids(spec_text: str) -> list[str]:
    """Acceptance-criterion ids defined in the Acceptance Criteria section."""
    return list(_chunks(_section(sections(spec_text), "Acceptance Criteria"), "AC"))


def check_spec(spec_path: Path) -> list[Check]:
    if not spec_path.exists():
        return [Check("spec_exists", False, f"הקובץ {spec_path.parent.name}/{spec_path.name} לא קיים")]
    text = spec_path.read_text(encoding="utf-8")
    secs = sections(text)
    found = [h for h, _ in secs]
    checks: list[Check] = []

    missing = [h for h in SPEC_HEADINGS if h.lower() not in (f.lower() for f in found)]
    order = [f for f in found if f.lower() in (h.lower() for h in SPEC_HEADINGS)]
    in_order = [h.lower() for h in order] == [h.lower() for h in SPEC_HEADINGS if h.lower() in (o.lower() for o in order)]
    checks.append(Check(
        "headings", not missing and in_order,
        "כל הכותרות קיימות ובסדר הנכון" if not missing and in_order
        else (f"כותרות חסרות: {', '.join(missing)}" if missing else "הכותרות לא בסדר של התבנית"),
    ))

    frs = _ids(_section(secs, "Functional Requirements"), "FR")
    checks.append(Check("fr_count", len(frs) >= 6, f"{len(frs)} דרישות פונקציונליות (נדרשות לפחות 6)"))

    nfr_chunks = _chunks(_section(secs, "Non-Functional Requirements"), "NFR")
    unmeasurable = [i for i, c in nfr_chunks.items() if not (re.search(r"\d", c.split(i, 1)[1]) and _UNIT.search(c))]
    nfr_ok = len(nfr_chunks) >= 3 and not unmeasurable
    msg = f"{len(nfr_chunks)} דרישות לא פונקציונליות (נדרשות לפחות 3, כל אחת עם מספר ויחידה)"
    if unmeasurable:
        msg += f"; בלי מספר או יחידה: {', '.join(unmeasurable)}"
    checks.append(Check("nfr_measurable", nfr_ok, msg))

    ac_text = _section(secs, "Acceptance Criteria")
    cited = set(_ids(ac_text, "FR"))
    uncited = [f for f in frs if f not in cited]
    checks.append(Check(
        "fr_cited_by_ac", bool(frs) and not uncited,
        "כל FR מופיע בקריטריון קבלה" if frs and not uncited else f"FR בלי קריטריון קבלה: {', '.join(uncited) or 'אין FR'}",
    ))

    ac_chunks = _chunks(ac_text, "AC")
    incomplete = [
        i for i, c in ac_chunks.items()
        if not all(re.search(rf"\b{w}\b", c, re.IGNORECASE) for w in ("given", "when", "then"))
    ]
    checks.append(Check(
        "ac_given_when_then", bool(ac_chunks) and not incomplete,
        f"{len(ac_chunks)} קריטריוני קבלה, כולם עם Given/When/Then" if ac_chunks and not incomplete
        else f"חסר Given/When/Then ב: {', '.join(incomplete) or 'אין קריטריוני קבלה'}",
    ))

    stake = _section(secs, "Stakeholders and Actors").lower()
    absent = [g for g, words in _STAKEHOLDER_GROUPS.items() if not any(w.lower() in stake for w in words)]
    checks.append(Check(
        "stakeholders", not absent,
        "בעלי העניין הנדרשים מופיעים" if not absent else f"חסרים בבעלי העניין: {', '.join(absent)}",
    ))

    oos = _section(secs, "Out of Scope")
    items = [ln for ln in oos.splitlines() if re.match(r"^\s*([-*+]|\d+[.)])\s+\S", ln)]
    checks.append(Check("out_of_scope", len(items) >= 3, f"{len(items)} פריטים מחוץ להיקף (נדרשים לפחות 3)"))

    diag = _section(secs, "Context Diagram")
    spec_dir = spec_path.parent
    files = [p for p in ("context.mmd", "context.png") if (spec_dir / p).exists()]
    referenced = [p for p in files if p in diag]
    checks.append(Check(
        "context_diagram", bool(referenced),
        "תרשים ההקשר קיים ומקושר" if referenced
        else "חסר spec/context.mmd או spec/context.png, או שהוא לא מוזכר תחת Context Diagram",
    ))
    return checks


def check_decision_log(path: Path) -> list[Check]:
    if not path.exists():
        return [Check("decision_log_exists", False, f"הקובץ {path.parent.name}/{path.name} לא קיים")]
    secs = sections(path.read_text(encoding="utf-8"))
    blocks: list[dict[str, str]] = []
    for heading, body in secs:
        if heading.lower() == "decision":
            blocks.append({})
        if blocks and heading.lower() in (f.lower() for f in DECISION_FIELDS):
            blocks[-1][heading.lower()] = body
    if not blocks:
        return [Check("decision_log_blocks", False, "לא נמצאה אף כותרת '## Decision'")]
    problems = []
    for n, block in enumerate(blocks, 1):
        for field in DECISION_FIELDS:
            if not block.get(field.lower(), "").strip():
                problems.append(f"החלטה {n}: השדה '{field}' חסר או ריק")
    if problems:
        return [Check("decision_log_fields", False, "; ".join(problems))]
    return [Check("decision_log_fields", True, f"{len(blocks)} החלטות, כל השדות מלאים")]
