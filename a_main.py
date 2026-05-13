



    
from pathlib import Path
from io import BytesIO
import sys

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from pypdf import PdfReader, PdfWriter
from pypdf.constants import UserAccessPermissions
from reportlab.pdfgen import canvas
from reportlab.lib.colors import Color

# =========================
# FONT REGISTRATION
# =========================

# Path to Arial TrueType font (adjust if needed)
ARIAL_TTF_PATH = r"C:\Windows\Fonts\arial.ttf"

# Register Arial under the name "Arial"
pdfmetrics.registerFont(TTFont("Arial", ARIAL_TTF_PATH))

# =========================
# CONFIGURATION FLAGS
# =========================

# If True, output PDF will require a password to open (stronger).
ENABLE_PASSWORD_PROTECTION: bool = False

# If True, try to set "no edit / no copy / no print" via PDF permissions
# without requiring a password to open. This is WEAK: many tools can ignore
# or remove it. Use ONLY for low-risk cases.
ENABLE_WEAK_PERMISSIONS_ONLY: bool = True

# If True, watermark overlay will be added.
ENABLE_WATERMARK: bool = True

# Password used when ENABLE_PASSWORD_PROTECTION is True.
PDF_PASSWORD: str = "change-this-password"

# Text for the diagonal watermark.
WATERMARK_TEXT: str = "PRIVATE DOCUMENT - DO NOT SHARE"

# Output suffix before ".pdf".
OUTPUT_SUFFIX: str = "_protected"

# Encryption algorithm.
# Options (pypdf docs): "RC4-40", "RC4-128", "AES-128", "AES-256-R5", "AES-256"
ENCRYPTION_ALGORITHM: str = "AES-256"

# SECURITY NOTE:
# - ENABLE_PASSWORD_PROTECTION uses a password and is stronger.
# - ENABLE_WEAK_PERMISSIONS_ONLY only sets PDF permission bits; many viewers
#   and tools can ignore or overwrite these. Use only as convenience, NOT real
#   security. [web:14][web:22][web:126]


def find_input_pdf(script_dir: Path, explicit_name: str | None = None) -> Path:
    """
    Decide which input PDF to use.

    - If explicit_name is provided, use that file.
    - Otherwise, find one .pdf in the script directory that is not already
      a protected output.
    """
    if explicit_name:
        pdf_path = script_dir / explicit_name
        if not pdf_path.exists():
            raise FileNotFoundError(f"File not found: {pdf_path}")
        if pdf_path.suffix.lower() != ".pdf":
            raise ValueError("The specified file is not a PDF.")
        return pdf_path

    pdf_files = sorted(
        p for p in script_dir.iterdir()
        if p.is_file()
        and p.suffix.lower() == ".pdf"
        and not p.stem.endswith(OUTPUT_SUFFIX)
    )

    if not pdf_files:
        raise FileNotFoundError("No PDF file found in the same folder as this script.")

    if len(pdf_files) > 1:
        names = ", ".join(p.name for p in pdf_files)
        raise RuntimeError(
            "Multiple PDF files found. Pass the filename as an argument. "
            f"Found: {names}"
        )

    return pdf_files[0]


def create_diagonal_text_overlay(width: float, height: float, text: str) -> BytesIO:
    """
    Create a 1-page PDF in memory with repeated diagonal text (around 45°),
    using Arial and larger letters.
    """
    packet = BytesIO()
    c = canvas.Canvas(packet, pagesize=(width, height))

    # Semi-transparent dark gray.
    c.setFillColor(Color(0.2, 0.2, 0.2, alpha=0.18))
    font_size = 28
    c.setFont("Arial", font_size)

    # Move origin to page center.
    c.saveState()
    c.translate(width / 2.0, height / 2.0)

    # Rotate canvas by 45 degrees.
    c.rotate(45)

    # After translate+rotate, origin is center; axes rotated.
    text_width = c.stringWidth(text, "Arial", font_size)

    # Vertical spacing between repeated lines along rotated axis.
    line_gap = 120

    # Approximate span to cover diagonal.
    half_span = max(width, height)

    y = -half_span
    while y < half_span:
        # Center text horizontally around origin.
        x = -text_width / 2.0
        c.drawString(x, y, text)
        y += line_gap

    c.restoreState()

    c.save()
    packet.seek(0)
    return packet


def protect_pdf(input_pdf: Path, password: str, watermark_text: str) -> Path:
    """
    Read input PDF, optionally add a watermark to each page, optionally
    apply encryption / permissions, and write output with OUTPUT_SUFFIX.
    """
    reader = PdfReader(str(input_pdf))
    writer = PdfWriter()

    # Process each page.
    for page in reader.pages:
        if ENABLE_WATERMARK:
            width = float(page.mediabox.width)
            height = float(page.mediabox.height)

            # Build overlay page in memory.
            overlay_stream = create_diagonal_text_overlay(width, height, watermark_text)
            overlay_pdf = PdfReader(overlay_stream)
            overlay_page = overlay_pdf.pages[0]

            # Merge overlay into the page.
            page.merge_page(overlay_page)

        writer.add_page(page)

    # Apply encryption / permissions depending on flags.
    if ENABLE_PASSWORD_PROTECTION:
        # Stronger: requires password to open.
        writer.encrypt(
            user_password=password,
            owner_password=None,
            algorithm=ENCRYPTION_ALGORITHM,
        )
    elif ENABLE_WEAK_PERMISSIONS_ONLY:
        # Weak: set permissions but do not require password.
        # According to examples, you can use permissions_flag bitmask;
        # 0 means "no permissions" in this context. [web:14][web:72][web:127][web:123]
        writer.encrypt(
            user_password="",
            owner_password="owner-only",
            permissions_flag=UserAccessPermissions(0),
            algorithm="RC4-128",
        )

    # Build output path and write file.
    output_pdf = input_pdf.with_name(f"{input_pdf.stem}{OUTPUT_SUFFIX}.pdf")
    with open(output_pdf, "wb") as f:
        writer.write(f)

    return output_pdf


def main() -> None:
    """
    Entry point: determine input PDF, run protection, print paths.
    """
    script_dir = Path(__file__).resolve().parent
    explicit_name = sys.argv[1] if len(sys.argv) > 1 else None

    input_pdf = find_input_pdf(script_dir, explicit_name)
    output_pdf = protect_pdf(input_pdf, PDF_PASSWORD, WATERMARK_TEXT)

    print(f"Input:  {input_pdf}")
    print(f"Output: {output_pdf}")


if __name__ == "__main__":
    main()
    



