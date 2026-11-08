# הקמת סביבת עבודה (Windows)

כל הפקודות ב־PowerShell, מתוך שורש המאגר (התיקייה שבה נמצא `README.md`).

## 1. לוודא ש־Python 3.12 מותקן

```powershell
py -3.12 --version
```

אמור להופיע `Python 3.12.x`. אם `py` לא מוכר, נסי `python --version`. אם זו לא 3.12, פני לטכנאי המעבדה.

## 2. ליצור סביבה וירטואלית

```powershell
py -3.12 -m venv .venv
```

נוצרת תיקייה `.venv`. היא לא נכנסת ל־git (ראי `.gitignore`).

## 3. להתקין את החבילות

```powershell
.venv\Scripts\python -m pip install -r requirements-dev.txt
```

אנחנו מריצות את `python` מתוך `.venv\Scripts\` ישירות. כך לא צריך "להפעיל" את הסביבה, ולא נתקעים על מדיניות ההרצה של PowerShell.
(מי שרוצה להפעיל: `.venv\Scripts\Activate.ps1`. אם יש שגיאה על execution policy — פשוט להמשיך בלי הפעלה.)

## 4. בדיקת תקינות

```powershell
.venv\Scripts\python -m tools.doctor
```

`doctor` בודק: גרסת Python, סביבה וירטואלית, חבילות מותקנות, UTF-8, SQLite, אזורי זמן. כל בעיה מגיעה עם הוראת תיקון.

## 5. הרצת הבדיקות

```powershell
.venv\Scripts\python -m pytest
```

בסוף מפגש 4 ההתחלתי אמור להופיע `3 passed`.

## 6. VS Code

`Ctrl+Shift+P` ← **Python: Select Interpreter** ← לבחור את המפרש שבתוך `.venv`.

## תקלות נפוצות

| אם קורה... | נסי... |
|---|---|
| `py` לא מוכר | `python --version`; אם 3.12, השתמשי ב־`python` במקום `py -3.12` |
| `doctor` מדווח גרסה אחרת | למחוק את `.venv` וליצור מחדש עם `py -3.12` |
| עברית מופיעה כ־`???` | להגדיר `PYTHONUTF8=1` (ההוראה המדויקת מופיעה ב־`doctor`) ולפתוח מסוף חדש |
| המאגר בתוך OneDrive | להעביר ל־`C:\dev\` |
| `pytest` לא מוצא מודול | להריץ משורש המאגר |
| `pip` נתקע | ייתכן סינון רשת במעבדה; לפנות לטכנאי |
