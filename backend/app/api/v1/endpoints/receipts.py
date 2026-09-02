"""Receipt Upload and Processing API endpoints."""
import logging
import uuid
import base64
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from pydantic import BaseModel

from app.services.workflow import run_receipt_workflow
from app.core.security import get_current_user_id

logger = logging.getLogger(__name__)

router = APIRouter()

# Define upload directory
UPLOAD_DIR = Path("data/receipts")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


class Base64ImageRequest(BaseModel):
    image_base64: str
    category_name: str = "Health Insurance"


@router.post("/upload", summary="Upload and process receipt image")
async def upload_receipt(
    file: UploadFile = File(...),
    category_name: str = Form("Health Insurance"),
    user_id: str = Depends(get_current_user_id)
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

        logger.info(f"File saved to: {file_path}")

        # Generate URL for serving the image
        receipt_url = f"/receipts/{unique_filename}"

        # Run the request through the compiled LangGraph workflow:
        # Inspector -> Validator -> Tax Expert -> Accountant
        result = run_receipt_workflow(
            user_id=user_id,
            image_path=str(file_path),
            image_url=receipt_url,
        )

        receipt_data = result.get("receipt_data", {})

        if receipt_data.get("error"):
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

        if result.get("status") == "awaiting_user_input":
            missing_fields = result.get("missing_fields", [])
            raise HTTPException(
                status_code=400,
                detail=f"Missing required fields in receipt: {', '.join(missing_fields)}"
            )

        save_result = result.get("accountant_result", {})

        if not save_result.get("success"):
            error_detail = save_result.get('error', 'Unknown error')
            logger.warning(f"Failed to save transaction: {error_detail}")
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
async def upload_receipt_base64(
    request: Base64ImageRequest,
    user_id: str = Depends(get_current_user_id)
):
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

        # Run the request through the compiled LangGraph workflow:
        # Inspector -> Validator -> Tax Expert -> Accountant
        result = run_receipt_workflow(
            user_id=user_id,
            image_bytes=image_bytes,
        )

        receipt_data = result.get("receipt_data", {})

        if receipt_data.get("error"):
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

        if result.get("status") == "awaiting_user_input":
            missing_fields = result.get("missing_fields", [])
            raise HTTPException(
                status_code=400,
                detail=f"Missing required fields in receipt: {', '.join(missing_fields)}"
            )

        save_result = result.get("accountant_result", {})

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
