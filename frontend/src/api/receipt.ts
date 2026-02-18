import { UploadReceiptRequest, UploadReceiptResponse } from '../types/receipt';

const API_BASE_URL = 'http://localhost:8000/api/v1';

export const receiptApi = {
  uploadReceipt: async (request: UploadReceiptRequest): Promise<UploadReceiptResponse> => {
    const formData = new FormData();
    formData.append('file', request.file);
    formData.append('user_id', request.user_id);
    
    // Only include category_name if explicitly provided
    // Otherwise, let backend auto-detect from receipt content
    if (request.category_name) {
      formData.append('category_name', request.category_name);
    }

    const response = await fetch(`${API_BASE_URL}/receipts/upload`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'Upload failed' }));
      throw new Error(errorData.detail || `Upload failed with status ${response.status}`);
    }

    return response.json();
  },
};
