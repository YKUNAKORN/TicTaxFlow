"""One-off generator for the two synthetic demo receipt images used by
seed_demo.py and DEMO.md. Not part of the app runtime -- requires Pillow,
which is intentionally NOT added to requirements.txt for that reason.

Run once (or whenever the demo receipts need to change):
    pip install Pillow
    python scripts/generate_sample_receipts.py

All merchant names, tax IDs, and amounts below are fictional and clearly
labelled "SAMPLE RECEIPT" on the image itself -- these are not real
invoices and must never be mistaken for one.
"""
import logging
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

OUT_DIR = Path(__file__).resolve().parent.parent / "data" / "fixtures" / "sample_receipts"

FONT_CANDIDATES = [
    r"C:\Windows\Fonts\arial.ttf",
    r"C:\Windows\Fonts\consola.ttf",
]


def _font(size: int) -> ImageFont.FreeTypeFont:
    for path in FONT_CANDIDATES:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    logger.warning("No TrueType font found, falling back to PIL default (small, may hurt OCR)")
    return ImageFont.load_default()


def render_receipt(out_path: Path, merchant: str, tax_id: str, date: str,
                    item: str, amount: float) -> None:
    width, height = 900, 700
    img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(img)

    title_font = _font(34)
    label_font = _font(26)
    value_font = _font(26)
    watermark_font = _font(20)

    y = 40
    draw.text((width // 2, y), merchant, font=title_font, fill="black", anchor="ma")
    y += 60
    draw.line([(60, y), (width - 60, y)], fill="black", width=2)
    y += 30

    rows = [
        ("Tax ID:", tax_id),
        ("Date:", date),
        ("Item:", item),
    ]
    for label, value in rows:
        draw.text((80, y), label, font=label_font, fill="black")
        draw.text((280, y), value, font=value_font, fill="black")
        y += 50

    y += 20
    draw.line([(60, y), (width - 60, y)], fill="black", width=2)
    y += 30
    draw.text((80, y), "TOTAL AMOUNT:", font=title_font, fill="black")
    draw.text((520, y), f"{amount:,.2f} THB", font=title_font, fill="black")

    draw.text((width // 2, height - 40), "SAMPLE RECEIPT -- FOR DEMO PURPOSES ONLY, NOT A REAL INVOICE",
               font=watermark_font, fill=(150, 150, 150), anchor="ma")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    img.save(out_path)
    logger.info("Wrote %s", out_path)


def main() -> None:
    render_receipt(
        OUT_DIR / "health_insurance_receipt.png",
        merchant="Bangkok Health Insurance Co., Ltd.",
        tax_id="0105561001234",
        date="2026-08-20",
        item="Health Insurance Premium Payment",
        amount=8500.00,
    )
    render_receipt(
        OUT_DIR / "life_insurance_topup_receipt.png",
        merchant="Muang Thai Life Insurance PCL",
        tax_id="0107537000123",
        date="2026-08-25",
        item="Life Insurance Premium Payment",
        amount=15000.00,
    )


if __name__ == "__main__":
    main()
