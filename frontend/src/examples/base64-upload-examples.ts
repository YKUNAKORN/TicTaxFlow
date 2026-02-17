// Frontend integration example for base64 upload API

// Example 1: Upload from file input
async function uploadReceiptFromFileInput(file: File, userId: string) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    
    reader.onload = async () => {
      const base64Image = reader.result as string;
      
      try {
        const response = await fetch('http://localhost:8000/api/v1/receipts/upload-base64', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            image_base64: base64Image,
            user_id: userId,
            category_name: 'Health Insurance'
          })
        });
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        resolve(data);
      } catch (error) {
        reject(error);
      }
    };
    
    reader.onerror = () => reject(reader.error);
    reader.readAsDataURL(file);
  });
}

// Example 2: Upload from canvas
async function uploadReceiptFromCanvas(canvas: HTMLCanvasElement, userId: string) {
  const base64Image = canvas.toDataURL('image/jpeg', 0.9);
  
  const response = await fetch('http://localhost:8000/api/v1/receipts/upload-base64', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      image_base64: base64Image,
      user_id: userId,
      category_name: 'Health Insurance'
    })
  });
  
  return await response.json();
}

// Example 3: Upload from camera capture
async function captureAndUploadReceipt(userId: string) {
  try {
    // Get camera stream
    const stream = await navigator.mediaDevices.getUserMedia({ 
      video: { facingMode: 'environment' } 
    });
    
    // Create video element
    const video = document.createElement('video');
    video.srcObject = stream;
    await video.play();
    
    // Capture frame to canvas
    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext('2d');
    ctx?.drawImage(video, 0, 0);
    
    // Stop camera
    stream.getTracks().forEach(track => track.stop());
    
    // Upload captured image
    const result = await uploadReceiptFromCanvas(canvas, userId);
    
    return result;
  } catch (error) {
    console.error('Camera capture failed:', error);
    throw error;
  }
}

// Example 4: Drag and drop with preview
function setupDragAndDrop(dropzoneId: string, userId: string) {
  const dropzone = document.getElementById(dropzoneId);
  if (!dropzone) return;
  
  dropzone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropzone.classList.add('drag-over');
  });
  
  dropzone.addEventListener('dragleave', () => {
    dropzone.classList.remove('drag-over');
  });
  
  dropzone.addEventListener('drop', async (e) => {
    e.preventDefault();
    dropzone.classList.remove('drag-over');
    
    const files = e.dataTransfer?.files;
    if (!files || files.length === 0) return;
    
    const file = files[0];
    
    // Validate file type
    if (!file.type.startsWith('image/')) {
      alert('Please upload an image file');
      return;
    }
    
    try {
      // Show loading state
      dropzone.classList.add('loading');
      
      // Upload file
      const result = await uploadReceiptFromFileInput(file, userId);
      
      console.log('Upload result:', result);
      
      // Show success message
      if (result.success) {
        alert('Receipt processed successfully');
        // Update UI with extracted data
        displayExtractedData(result.data.extracted_data);
        displayTransaction(result.data.transaction);
      }
    } catch (error) {
      console.error('Upload failed:', error);
      alert('Failed to process receipt');
    } finally {
      dropzone.classList.remove('loading');
    }
  });
}

// Helper: Display extracted data
function displayExtractedData(data: any) {
  console.log('Extracted Data:', {
    date: data.date,
    amount: data.amount,
    tax_id: data.tax_id
  });
  
  // Update UI elements
  document.getElementById('receipt-date')!.textContent = data.date || 'N/A';
  document.getElementById('receipt-amount')!.textContent = `${data.amount} THB` || 'N/A';
  document.getElementById('receipt-tax-id')!.textContent = data.tax_id || 'N/A';
}

// Helper: Display transaction details
function displayTransaction(transaction: any) {
  console.log('Transaction:', {
    id: transaction.id,
    deductible_amount: transaction.deductible_amount,
    status: transaction.status
  });
  
  // Update UI elements
  document.getElementById('transaction-id')!.textContent = transaction.id;
  document.getElementById('deductible-amount')!.textContent = `${transaction.deductible_amount} THB`;
  document.getElementById('transaction-status')!.textContent = transaction.status;
}

// Example 5: React component
import React, { useState } from 'react';

interface UploadResult {
  success: boolean;
  message: string;
  data: {
    extracted_data: {
      date: string;
      amount: number;
      tax_id: string;
    };
    transaction: any;
  };
}

export const ReceiptUploader: React.FC<{ userId: string }> = ({ userId }) => {
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState<UploadResult | null>(null);
  
  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    
    setUploading(true);
    
    try {
      const uploadResult = await uploadReceiptFromFileInput(file, userId);
      setResult(uploadResult as UploadResult);
    } catch (error) {
      console.error('Upload failed:', error);
      alert('Failed to process receipt');
    } finally {
      setUploading(false);
    }
  };
  
  return (
    <div>
      <input 
        type="file" 
        accept="image/*" 
        onChange={handleFileChange}
        disabled={uploading}
      />
      
      {uploading && <p>Processing receipt...</p>}
      
      {result?.success && (
        <div>
          <h3>Receipt Processed Successfully</h3>
          <p>Date: {result.data.extracted_data.date}</p>
          <p>Amount: {result.data.extracted_data.amount} THB</p>
          <p>Tax ID: {result.data.extracted_data.tax_id}</p>
          <p>Deductible: {result.data.transaction.deductible_amount} THB</p>
        </div>
      )}
    </div>
  );
};
