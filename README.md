


# pdf-passport-protector

Small Python script to watermark and protect a PDF (e.g. a passport scan) in the same folder.

---

## What it does

- Finds one `.pdf` in the script folder (or uses a file you pass as argument).
- Adds a big diagonal Arial watermark: `PRIVATE DOCUMENT - DO NOT SHARE`.
- Can add a password to open the PDF.
- Can set weak “no edit / no copy / no print” flags (not real security).
- Saves as `<name>_protected.pdf` in the same folder.

---

## Install

```bash
pip install pypdf reportlab cryptography
```

On Windows, this assumes Arial at:

```text
C:\Windows\Fonts\arial.ttf
```

Change `ARIAL_TTF_PATH` in `code.py` if needed. [web:89][web:90]

---

## Configure

Edit flags at the top of `code.py`:

```python
ENABLE_PASSWORD_PROTECTION = True      # require password to open
ENABLE_WEAK_PERMISSIONS_ONLY = False   # no-edit flags, no password (weak)
ENABLE_WATERMARK = True                # draw diagonal watermark

PDF_PASSWORD = "change-this-password"
WATERMARK_TEXT = "PRIVATE DOCUMENT - DO NOT SHARE"
OUTPUT_SUFFIX = "_protected"
ENCRYPTION_ALGORITHM = "AES-256"
```

Typical modes:

- Strong: password + watermark

  ```python
  ENABLE_PASSWORD_PROTECTION = True
  ENABLE_WEAK_PERMISSIONS_ONLY = False
  ```

- Weak flags only (no password) + watermark

  ```python
  ENABLE_PASSWORD_PROTECTION = False
  ENABLE_WEAK_PERMISSIONS_ONLY = True
  ```

- Watermark only

  ```python
  ENABLE_PASSWORD_PROTECTION = False
  ENABLE_WEAK_PERMISSIONS_ONLY = False
  ```

---

## Use

From the folder with `code.py` and your PDF:

```bash
python code.py
# or
python code.py passport.pdf
```

The script prints input and output paths.

---

## Security notes

- Watermark is just visual.
- Password mode = normal PDF password protection via `pypdf`. [web:74]
- Weak mode uses permissions flags; many tools ignore or strip them. [web:112][web:118][web:122]
- This does not stop screenshots or photos of the screen.
