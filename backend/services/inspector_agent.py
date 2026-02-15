import os
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

# Initialize Gemini client
google_api = os.getenv("GEMINI_API_KEY")
genai_client = genai.Client(api_key=google_api)


def load_image(image_path):
    """Load image file and return as bytes."""
    try:
        with open(image_path, "rb") as f:
            return f.read()
    except Exception as e:
        print(f"Error loading image: {e}")
        return None


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
    
    # Load image
    image_data = load_image(image_path)
    
    if image_data is None:
        return "Failed to load image."
    
    # Use custom prompt or default
    prompt = custom_prompt if custom_prompt else build_inspector_prompt()
    
    # Prepare content with image
    try:
        response = genai_client.models.generate_content(
            model="gemini-2.5-flash",
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
    
    # Supported image formats
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
            model="gemini-2.5-flash",
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


def main():
    """Test the inspector agent."""
    print("Tax Document Inspector Agent")
    print("=" * 60)
    
    # Example usage
    test_image = "../data/receipts/sample_receipt.jpg"
    
    if os.path.exists(test_image):
        print(f"\nAnalyzing: {test_image}")
        result = inspect_document(test_image)
        print(f"\nResult:\n{result}")
        print("-" * 60)
    else:
        print(f"\nNo test image found at: {test_image}")
        print("Place receipt images in backend/data/receipts/ to test")
    
    print("\nInspector Agent ready!")


if __name__ == "__main__":
    main()
