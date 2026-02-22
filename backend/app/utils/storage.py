"""Supabase Storage utilities for receipt image uploads."""
from app.database.database import supabase

BUCKET_NAME = "receipts"


def upload_receipt_image(file_bytes: bytes, filename: str, user_id: str) -> str:
    """Upload a receipt image to Supabase Storage.

    The file is stored under <user_id>/<filename> inside the 'receipts' bucket.

    Args:
        file_bytes: Raw image bytes.
        filename: Desired filename (e.g. "receipt_001.jpg").
        user_id: UUID of the owning user, used as the folder prefix.

    Returns:
        Public URL of the uploaded image.

    Raises:
        RuntimeError: If the upload or URL retrieval fails.
    """
    storage_path = f"{user_id}/{filename}"

    try:
        supabase.storage.from_(BUCKET_NAME).upload(
            path=storage_path,
            file=file_bytes,
            file_options={"content-type": "image/jpeg", "upsert": "true"},
        )
    except Exception as e:
        raise RuntimeError(f"Failed to upload image to storage: {e}")

    try:
        res = supabase.storage.from_(BUCKET_NAME).get_public_url(storage_path)
        return res
    except Exception:
        # Fallback to a signed URL valid for 1 hour if public access is disabled
        try:
            res = supabase.storage.from_(BUCKET_NAME).create_signed_url(
                storage_path, expires_in=3600
            )
            return res.get("signedURL", "")
        except Exception as e:
            raise RuntimeError(f"Failed to get URL for uploaded image: {e}")
