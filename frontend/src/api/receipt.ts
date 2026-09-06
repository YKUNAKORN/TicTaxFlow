import { UploadReceiptRequest, UploadReceiptResponse } from '../types/receipt';
import { storage } from '../lib/storage';
import { API_BASE_URL } from './client';

export const receiptApi = {
  uploadReceipt: async (request: UploadReceiptRequest): Promise<UploadReceiptResponse> => {
    const formData = new FormData();
    formData.append('file', request.file);

    // Only include category_name if explicitly provided
    // Otherwise, let backend auto-detect from receipt content
    if (request.category_name) {
      formData.append('category_name', request.category_name);
    }

    const token = storage.getToken();

    const response = await fetch(`${API_BASE_URL}/receipts/upload`, {
      method: 'POST',
      headers: token ? { Authorization: `Bearer ${token}` } : undefined,
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'Upload failed' }));
      throw new Error(errorData.detail || `Upload failed with status ${response.status}`);
    }

    return response.json();
  },
};
