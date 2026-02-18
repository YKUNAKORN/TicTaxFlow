import React, { useState, useRef, DragEvent, ChangeEvent } from 'react';
import { UploadCloud, FileUp, CheckCircle2, XCircle, Loader2 } from 'lucide-react';
import { receiptApi } from '../../api';
import { storage } from '../../lib/storage';

interface UploadStatus {
  status: 'idle' | 'uploading' | 'success' | 'error';
  message?: string;
  fileName?: string;
}

interface UploadZoneProps {
  onUploadSuccess?: () => void;
}

const UploadZone: React.FC<UploadZoneProps> = ({ onUploadSuccess }) => {
    const [uploadStatus, setUploadStatus] = useState<UploadStatus>({ status: 'idle' });
    const [isDragging, setIsDragging] = useState(false);
    const fileInputRef = useRef<HTMLInputElement>(null);

    const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'application/pdf'];
    const maxSizeMB = 10;

    const validateFile = (file: File): string | null => {
        if (!allowedTypes.includes(file.type)) {
            return 'Invalid file type. Please upload PDF, JPG, or PNG files.';
        }
        
        const sizeMB = file.size / (1024 * 1024);
        if (sizeMB > maxSizeMB) {
            return `File size exceeds ${maxSizeMB}MB limit.`;
        }
        
        return null;
    };

    const handleFileUpload = async (file: File) => {
        const validationError = validateFile(file);
        if (validationError) {
            setUploadStatus({ 
                status: 'error', 
                message: validationError,
                fileName: file.name 
            });
            return;
        }

        const userId = storage.getUserId();
        if (!userId) {
            setUploadStatus({ 
                status: 'error', 
                message: 'Please log in to upload receipts.',
                fileName: file.name 
            });
            return;
        }

        setUploadStatus({ 
            status: 'uploading', 
            message: 'Processing receipt...',
            fileName: file.name 
        });

        try {
            const response = await receiptApi.uploadReceipt({
                file,
                user_id: userId
            });

            setUploadStatus({ 
                status: 'success', 
                message: 'Receipt processed successfully!',
                fileName: file.name 
            });

            // Wait for database to commit before refreshing dashboard
            setTimeout(() => {
                if (onUploadSuccess) {
                    onUploadSuccess();
                }
            }, 500);

            setTimeout(() => {
                setUploadStatus({ status: 'idle' });
            }, 3000);

        } catch (error) {
            let errorMessage = 'Upload failed. Please try again.';
            
            if (error instanceof Error) {
                errorMessage = error.message;
                
                // Provide helpful messages for specific errors
                if (errorMessage.includes('AI service configuration')) {
                    errorMessage = 'AI service is not configured. Please contact administrator.';
                } else if (errorMessage.includes('API key')) {
                    errorMessage = 'AI service error. Please contact administrator.';
                }
            }
            
            setUploadStatus({ 
                status: 'error', 
                message: errorMessage,
                fileName: file.name 
            });
        }
    };

    const handleDragOver = (e: DragEvent<HTMLDivElement>) => {
        e.preventDefault();
        setIsDragging(true);
    };

    const handleDragLeave = (e: DragEvent<HTMLDivElement>) => {
        e.preventDefault();
        setIsDragging(false);
    };

    const handleDrop = (e: DragEvent<HTMLDivElement>) => {
        e.preventDefault();
        setIsDragging(false);

        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFileUpload(files[0]);
        }
    };

    const handleFileInputChange = (e: ChangeEvent<HTMLInputElement>) => {
        const files = e.target.files;
        if (files && files.length > 0) {
            handleFileUpload(files[0]);
        }
    };

    const handleClick = () => {
        if (uploadStatus.status !== 'uploading') {
            fileInputRef.current?.click();
        }
    };

    const getStatusColor = () => {
        switch (uploadStatus.status) {
            case 'uploading': return 'border-blue-500 bg-blue-50/50';
            case 'success': return 'border-green-500 bg-green-50/50';
            case 'error': return 'border-red-500 bg-red-50/50';
            default: return isDragging ? 'border-blue-500 bg-blue-50/50' : 'border-slate-300 bg-slate-50';
        }
    };

    const renderContent = () => {
        switch (uploadStatus.status) {
            case 'uploading':
                return (
                    <div className="flex flex-col items-center justify-center pt-5 pb-6 text-center">
                        <div className="p-4 rounded-full bg-white shadow-sm mb-3">
                            <Loader2 size={32} className="text-blue-500 animate-spin" />
                        </div>
                        <p className="mb-2 text-sm font-medium text-slate-700">
                            Processing receipt...
                        </p>
                        <p className="text-xs text-slate-500">
                            {uploadStatus.fileName}
                        </p>
                    </div>
                );
            
            case 'success':
                return (
                    <div className="flex flex-col items-center justify-center pt-5 pb-6 text-center">
                        <div className="p-4 rounded-full bg-white shadow-sm mb-3">
                            <CheckCircle2 size={32} className="text-green-500" />
                        </div>
                        <p className="mb-2 text-sm font-medium text-green-700">
                            {uploadStatus.message}
                        </p>
                        <p className="text-xs text-slate-500">
                            {uploadStatus.fileName}
                        </p>
                    </div>
                );
            
            case 'error':
                return (
                    <div className="flex flex-col items-center justify-center pt-5 pb-6 text-center">
                        <div className="p-4 rounded-full bg-white shadow-sm mb-3">
                            <XCircle size={32} className="text-red-500" />
                        </div>
                        <p className="mb-2 text-sm font-medium text-red-700">
                            {uploadStatus.message}
                        </p>
                        <p className="text-xs text-slate-500 mb-2">
                            {uploadStatus.fileName}
                        </p>
                        <button 
                            onClick={() => setUploadStatus({ status: 'idle' })}
                            className="text-xs text-blue-600 hover:underline"
                        >
                            Try again
                        </button>
                    </div>
                );
            
            default:
                return (
                    <div className="flex flex-col items-center justify-center pt-5 pb-6 text-center">
                        <div className="p-4 rounded-full bg-white shadow-sm mb-3 group-hover:scale-110 transition-transform">
                            <UploadCloud size={32} className="text-blue-500" />
                        </div>
                        <p className="mb-2 text-sm font-medium text-slate-700">
                            <span className="text-blue-600 font-semibold hover:underline">Click to upload</span> or drag and drop
                        </p>
                        <p className="text-xs text-slate-500">
                            PDF, JPG, PNG (max. 10MB) - e-Tax Invoices supported
                        </p>
                    </div>
                );
        }
    };

    return (
        <div className="mb-8">
            <div 
                className="relative group cursor-pointer"
                onClick={handleClick}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
            >
                <div className={`
          flex flex-col items-center justify-center w-full h-48 
          rounded-xl border-2 border-dashed
          transition-all duration-200 ease-in-out
          group-hover:border-blue-500
          ${getStatusColor()}
        `}>
                    {renderContent()}
                </div>
                <input
                    ref={fileInputRef}
                    type="file"
                    accept=".pdf,.jpg,.jpeg,.png"
                    onChange={handleFileInputChange}
                    className="hidden"
                />
            </div>
        </div>
    );
};

export default UploadZone;
