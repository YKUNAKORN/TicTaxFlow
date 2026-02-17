"""Inspector Agent for receipt and document analysis."""
import os
import json
from pathlib import Path
from google import genai
from google.genai import types

from app.core.config import settings


genai_client = genai.Client(api_key=settings.GEMINI_API_KEY)


def load_image(image_path):
    """Load image file and return as bytes."""
    try:
        with open(image_path, "rb") as f:
            return f.read()
    except Exception as e:
        print(f"Error loading image: {e}")
        return None


def extract_receipt_from_bytes(image_data: bytes):
    """Extract receipt data from image bytes (supports base64)."""
    prompt = """Analyze this receipt or e-Tax invoice image and extract the following information.
Return ONLY a valid JSON object with these exact fields:

{
  "date": "YYYY-MM-DD format or original format if clear",
  "amount": "numeric value only (e.g., 1234.50)",
  "tax_id": "vendor tax identification number"
}

Rules:
- If a field is not found or unclear, use null
- For amount: extract the final total/grand total as a number
- For tax_id: extract the vendor's tax ID (not customer's)
- Return ONLY the JSON object, no additional text

JSON:"""
    
    try:
        response = genai_client.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=[
                types.Part.from_bytes(
                    data=image_data,
                    mime_type="image/jpeg"
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
            print(f"JSON parse error: {e}")
            return {
                "error": "Failed to parse JSON",
                "raw_response": response_text
            }
    
    except Exception as e:
        print(f"Error extracting data: {e}")
        return {"error": str(e)}


def extract_receipt_json(image_path):
    """Extract receipt data as JSON structure from file path."""
    print(f"Extracting data from: {image_path}")
    
    image_data = load_image(image_path)
    
    if image_data is None:
        return {"error": "Failed to load image"}
    
    return extract_receipt_from_bytes(image_data)


def build_inspector_prompt():
    """Build prompt for receipt/document inspection."""
    prompt = """You are a Tax Document Inspector for Thai tax system.

Analyze this image and extract the following information:

1. Document Type (receipt, invoice, tax document, etc.)
2. Vendor/Store Name
3. Date
4. Total Amount
5. Tax-related Information (VAT, tax ID, etc.)
6. Items/Services (if visible)
7. Payment Method (if visible)
8. Tax Deduction Eligibility (can this be used for tax deduction?)

Provide the information in a structured format.
If any information is not visible or unclear, state "Not found" or "Unclear".

Analysis:"""
    
    return prompt


def inspect_document(image_path, custom_prompt=None):
    """Inspect a document/receipt image using Gemini Vision."""
    print(f"Inspecting: {image_path}")
    
    image_data = load_image(image_path)
    
    if image_data is None:
        return "Failed to load image."
    
    prompt = custom_prompt if custom_prompt else build_inspector_prompt()
    
    try:
        response = genai_client.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=[
                types.Part.from_bytes(
                    data=image_data,
                    mime_type="image/jpeg"
                ),
                prompt
            ]
        )
        
        return response.text
    
    except Exception as e:
        print(f"Error analyzing image: {e}")
        return f"Error: {str(e)}"


def inspect_receipt_batch(image_folder):
    """Inspect multiple receipts in a folder."""
    folder_path = Path(image_folder)
    
    if not folder_path.exists():
        print(f"Folder not found: {image_folder}")
        return []
    
    image_extensions = [".jpg", ".jpeg", ".png", ".webp"]
    results = []
    
    for image_file in folder_path.iterdir():
        if image_file.suffix.lower() in image_extensions:
            result = inspect_document(str(image_file))
            results.append({
                "file": image_file.name,
                "analysis": result
            })
    
    return results


def extract_amount(image_path):
    """Quick extraction of total amount from receipt."""
    print(f"Extracting amount from: {image_path}")
    
    image_data = load_image(image_path)
    
    if image_data is None:
        return "Failed to load image."
    
    prompt = """Extract only the total amount from this receipt/document.
Return just the number with currency (e.g., "1,234.50 THB" or "1,234.50 Baht").
If multiple amounts are shown, return the final total/grand total.
If amount is not clear, return "Amount not found"."""
    
    try:
        response = genai_client.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=[
                types.Part.from_bytes(
                    data=image_data,
                    mime_type="image/jpeg"
                ),
                prompt
            ]
        )
        
        return response.text.strip()
    
    except Exception as e:
        print(f"Error extracting amount: {e}")
        return f"Error: {str(e)}"


def extract_receipts_batch_json(image_folder):
    """Extract JSON data from multiple receipts in a folder."""
    folder_path = Path(image_folder)
    
    if not folder_path.exists():
        print(f"Folder not found: {image_folder}")
        return []
    
    image_extensions = [".jpg", ".jpeg", ".png", ".webp"]
    results = []
    
    for image_file in folder_path.iterdir():
        if image_file.suffix.lower() in image_extensions:
            data = extract_receipt_json(str(image_file))
            results.append({
                "file": image_file.name,
                "data": data
            })
    
    return results


def main():
    """Test the inspector agent."""
    print("Tax Document Inspector Agent")
    print("=" * 60)
    
    test_image = settings.RECEIPTS_DIR / "sample_receipt.jpg"
    
    if test_image.exists():
        print(f"\n1. JSON Extraction:")
        print(f"   File: {test_image}")
        json_result = extract_receipt_json(str(test_image))
        print(f"   Result: {json.dumps(json_result, indent=2, ensure_ascii=False)}")
        print("-" * 60)
        
        print(f"\n2. Full Analysis:")
        result = inspect_document(str(test_image))
        print(f"   Result:\n{result}")
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
