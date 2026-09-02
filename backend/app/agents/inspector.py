"""Inspector Agent for receipt and document analysis."""
import json
import logging
from google import genai
from google.genai import types

from app.core.config import settings

logger = logging.getLogger(__name__)

genai_client = genai.Client(api_key=settings.GEMINI_API_KEY)

# Formats Gemini can actually analyze here, keyed to the magic bytes that
# identify them. Keep this in sync with receipts.py's upload validation.
SUPPORTED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp", "application/pdf"}

EXTENSION_FOR_MIME_TYPE = {
    "image/jpeg": "jpg",
    "image/png": "png",
    "image/webp": "webp",
    "application/pdf": "pdf",
}


def detect_mime_type(data: bytes) -> str:
    """Detect a file's real MIME type from its magic bytes.

    Trusting a client-supplied filename/Content-Type is not enough: Gemini
    needs an accurate mime_type to decode inline file data, and a mislabeled
    file (e.g. a PNG uploaded as "photo.jpg") would otherwise be sent to
    Gemini as the wrong type and silently misbehave.
    """
    if data[:3] == b"\xff\xd8\xff":
        return "image/jpeg"
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        return "image/png"
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "image/webp"
    if data[:5] == b"%PDF-":
        return "application/pdf"
    return "application/octet-stream"


def load_image(image_path):
    """Load image file and return as bytes."""
    try:
        with open(image_path, "rb") as f:
            return f.read()
    except Exception as e:
        logger.error("Error loading image: %s", e)
        return None


def extract_receipt_from_bytes(image_data: bytes, mime_type: str = None):
    """Extract receipt data from file bytes (supports base64)."""
    mime_type = mime_type or detect_mime_type(image_data)
    prompt = """Analyze this receipt or e-Tax invoice image and extract the following information.
Return ONLY a valid JSON object with these exact fields:

{
  "date": "YYYY-MM-DD",
  "amount": 0.00,
  "tax_id": "vendor tax identification number",
  "merchant_name": "name of the merchant or store"
}

Rules:
- If a field is not found or unclear, use null
- For date: use YYYY-MM-DD format
- For amount: extract the final total/grand total as a number (not a string)
- For tax_id: extract the vendor's tax ID (not customer's)
- For merchant_name: extract the business/store name
- Do NOT classify or categorize the receipt
- Return ONLY the JSON object, no additional text

JSON:"""
    
    try:
        response = genai_client.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=[
                types.Part.from_bytes(
                    data=image_data,
                    mime_type=mime_type
                ),
                prompt
            ]
        )

        response_text = response.text.strip()
        
        # Remove markdown code blocks if present
        if response_text.startswith("```"):
            response_text = response_text.split("```")[1]
            if response_text.startswith("json"):
                response_text = response_text[4:]
            response_text = response_text.strip()
        
        # Parse JSON
        try:
            data = json.loads(response_text)
            return data
        except json.JSONDecodeError as e:
            logger.error("JSON parse error: %s", e)
            return {
                "error": "Failed to parse JSON",
                "raw_response": response_text
            }

    except Exception as e:
        logger.error("Error extracting data: %s", e)
        return {"error": str(e)}


def extract_receipt_json(image_path):
    """Extract receipt data as JSON structure from file path."""
    logger.info("Extracting data from: %s", image_path)

    image_data = load_image(image_path)

    if image_data is None:
        return {"error": "Failed to load image"}

    return extract_receipt_from_bytes(image_data, mime_type=detect_mime_type(image_data))


def main():
    """Test the inspector agent."""
    print("Tax Document Inspector Agent")
    print("=" * 60)
    
    test_image = settings.RECEIPTS_DIR / "sample_receipt.jpg"
    
    if test_image.exists():
        print(f"\nJSON Extraction:")
        print(f"   File: {test_image}")
        json_result = extract_receipt_json(str(test_image))
        print(f"   Result: {json.dumps(json_result, indent=2, ensure_ascii=False)}")
        print("-" * 60)
    else:
        print(f"\nNo test image found at: {test_image}")
        print("Place receipt images in backend/data/receipts/ to test")
        print("\nExample usage:")
        print("  from app.agents.inspector import extract_receipt_json")
        print('  data = extract_receipt_json("receipt.jpg")')
        print('  print(data["date"], data["amount"], data["tax_id"])')
    
    print("\nInspector Agent ready!")


if __name__ == "__main__":
    main()
