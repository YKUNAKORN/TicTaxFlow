import React from 'react';
import { Construction } from 'lucide-react';

const TransactionsPage: React.FC = () => {
    return (
        <div className="flex flex-col items-center justify-center min-h-[60vh] text-center">
            <div className="h-16 w-16 bg-blue-50 rounded-full flex items-center justify-center mb-6">
                <Construction size={32} className="text-blue-500" />
            </div>
            <h2 className="text-2xl font-bold text-slate-900 mb-2">Transactions History</h2>
            <p className="text-slate-500 max-w-md">
                This page will contain the full history of all uploaded receipts and their status.
            </p>
        </div>
    );
};

export default TransactionsPage;
