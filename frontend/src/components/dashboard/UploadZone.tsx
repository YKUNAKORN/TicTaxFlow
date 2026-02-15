import React from 'react';
import { UploadCloud, FileUp } from 'lucide-react';

const UploadZone: React.FC = () => {
    return (
        <div className="mb-8">
            <div className="relative group cursor-pointer">
                <div className="
          flex flex-col items-center justify-center w-full h-48 
          rounded-xl border-2 border-dashed border-slate-300 bg-slate-50 
          transition-all duration-200 ease-in-out
          group-hover:border-blue-500 group-hover:bg-blue-50/50
        ">
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
                </div>
            </div>
        </div>
    );
};

export default UploadZone;
