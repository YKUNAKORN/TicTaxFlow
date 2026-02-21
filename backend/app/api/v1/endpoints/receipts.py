"""Receipt Upload and Processing API endpoints."""
import os
import uuid
import base64
from pathlib import Path
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import Optional
from pydantic import BaseModel

from app.agents.inspector import extract_receipt_json, extract_receipt_from_bytes
from app.agents.accountant import save_receipt_from_inspector
from app.agents.tax_expert import ask_tax_expert

router = APIRouter()

# Define upload directory
UPLOAD_DIR = Path("data/receipts")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


class Base64ImageRequest(BaseModel):
    image_base64: str
    user_id: str
    category_name: str = "Health Insurance"


@router.post("/upload", summary="Upload and process receipt image")
async def upload_receipt(
    file: UploadFile = File(...),
    user_id: str = Form(...),
    category_name: str = Form("Health Insurance")
):
    """
    Upload a receipt image and automatically extract data using AI
    
    Steps:
    1. Save uploaded image to disk
    2. Extract receipt data using Inspector Agent (Gemini Vision)
    3. Save transaction to database using Accountant Agent
    
    Returns: Extracted data and transaction details
    """
    
    # Validate file type
    allowed_types = ["image/jpeg", "image/jpg", "image/png", "image/webp"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {', '.join(allowed_types)}"
        )
    
    try:
        # Generate unique filename
        file_extension = file.filename.split(".")[-1]
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        file_path = UPLOAD_DIR / unique_filename
        
        # Save file to disk
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        print(f"File saved to: {file_path}")
        
        # Generate URL for serving the image
        receipt_url = f"/receipts/{unique_filename}"
        
        # Extract data using Inspector Agent
        receipt_data = extract_receipt_json(str(file_path))
        
        if "error" in receipt_data:
            error_msg = receipt_data.get('error', 'Unknown error')
            
            # Provide user-friendly error messages
            if 'API key not valid' in str(error_msg) or 'API_KEY_INVALID' in str(error_msg):
                raise HTTPException(
                    status_code=503,
                    detail="AI service configuration error. Please contact administrator to set up the API key."
                )
            
            raise HTTPException(
                status_code=400,
                detail=f"Failed to extract receipt data: {error_msg}"
            )
        
        # Use Tax Expert (RAG) to classify the receipt
        tax_result = ask_tax_expert(receipt_data)
        final_category = tax_result.get("category", "None")

        print(f"Tax Expert classification: {final_category}")
        print(f"Extracted receipt data: {receipt_data}")

        # Save to database using Accountant Agent
        save_result = save_receipt_from_inspector(
            user_id=user_id,
            receipt_data=receipt_data,
            category_name=final_category,
            receipt_image_url=receipt_url
        )
        
        print(f"Save result: {save_result}")
        
        if not save_result.get("success"):
            error_detail = save_result.get('error', 'Unknown error')
            print(f"Failed to save transaction: {error_detail}")
            raise HTTPException(
                status_code=400,
                detail=f"Failed to save transaction: {error_detail}"
            )
        
        return {
            "success": True,
            "message": "Receipt processed successfully",
            "data": {
                "file_path": str(file_path),
                "extracted_data": receipt_data,
                "transaction": save_result.get("data")
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process receipt: {str(e)}"
        )


@router.post("/upload-base64", summary="Upload receipt as base64 image")
async def upload_receipt_base64(request: Base64ImageRequest):
    """
    Upload a receipt image as base64 string and process it
    
    Frontend can send image directly from:
    - File reader (FileReader API)
    - Canvas (canvas.toDataURL())
    - Camera capture
    
    Steps:
    1. Decode base64 to bytes
    2. Extract receipt data using Inspector Agent (Gemini Vision)
    3. Save transaction to database using Accountant Agent
    """
    
    try:
        # Remove data URI prefix if present
        # "data:image/jpeg;base64,..." -> "..."
        if "base64," in request.image_base64:
            base64_str = request.image_base64.split("base64,")[1]
        else:
            base64_str = request.image_base64
        
        # Decode base64 to bytes
        image_bytes = base64.b64decode(base64_str)
        
        # Extract data using Inspector Agent with bytes
        receipt_data = extract_receipt_from_bytes(image_bytes)
        
        if "error" in receipt_data:
            error_msg = receipt_data.get('error', 'Unknown error')
            
            # Provide user-friendly error messages
            if 'API key not valid' in str(error_msg) or 'API_KEY_INVALID' in str(error_msg):
                raise HTTPException(
                    status_code=503,
                    detail="AI service configuration error. Please contact administrator to set up the API key."
                )
            
            raise HTTPException(
                status_code=400,
                detail=f"Failed to extract receipt data: {error_msg}"
            )
        
        # Use Tax Expert (RAG) to classify the receipt
        tax_result = ask_tax_expert(receipt_data)
        final_category = tax_result.get("category", "None")

        print(f"Tax Expert classification: {final_category}")

        # Save to database using Accountant Agent
        save_result = save_receipt_from_inspector(
            user_id=request.user_id,
            receipt_data=receipt_data,
            category_name=final_category,
            receipt_image_url=None
        )
        
        if not save_result.get("success"):
            raise HTTPException(
                status_code=400,
                detail=f"Failed to save transaction: {save_result.get('error')}"
            )
        
        return {
            "success": True,
            "message": "Receipt processed successfully",
            "data": {
                "extracted_data": receipt_data,
                "transaction": save_result.get("data")
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process receipt: {str(e)}"
        )


@router.post("/process-image", summary="Process receipt from image path")
async def process_receipt_from_path(
    image_path: str = Form(...),
    user_id: str = Form(...),
    category_name: str = Form("Health Insurance")
):
    """
    Process a receipt from an existing image path
    Useful for testing or batch processing
    """
    
    # Check if file exists
    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail="Image file not found")
    
    try:
        # Extract data using Inspector Agent
        receipt_data = extract_receipt_json(image_path)
        
        if "error" in receipt_data:
            error_msg = receipt_data.get('error', 'Unknown error')
            
            # Provide user-friendly error messages
            if 'API key not valid' in str(error_msg) or 'API_KEY_INVALID' in str(error_msg):
                raise HTTPException(
                    status_code=503,
                    detail="AI service configuration error. Please contact administrator to set up the API key."
                )
            
            raise HTTPException(
                status_code=400,
                detail=f"Failed to extract receipt data: {error_msg}"
            )
        
        # Use Tax Expert (RAG) to classify the receipt
        tax_result = ask_tax_expert(receipt_data)
        final_category = tax_result.get("category", "None")

        print(f"Tax Expert classification: {final_category}")

        # Save to database using Accountant Agent
        save_result = save_receipt_from_inspector(
            user_id=user_id,
            receipt_data=receipt_data,
            category_name=final_category,
            receipt_image_url=image_path
        )
        
        if not save_result.get("success"):
            raise HTTPException(
                status_code=400,
                detail=f"Failed to save transaction: {save_result.get('error')}"
            )
        
        return {
            "success": True,
            "message": "Receipt processed successfully",
            "data": {
                "extracted_data": receipt_data,
                "transaction": save_result.get("data")
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process receipt: {str(e)}"
        )
