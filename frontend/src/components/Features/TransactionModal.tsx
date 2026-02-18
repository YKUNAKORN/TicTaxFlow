import React from 'react';
import { X, CheckCircle, BrainCircuit } from 'lucide-react';
import { Transaction } from '../../data/mockData';
import { clsx } from 'clsx';

interface TransactionModalProps {
    transaction: Transaction | null;
    isOpen: boolean;
    onClose: () => void;
}

const TransactionModal: React.FC<TransactionModalProps> = ({ transaction, isOpen, onClose }) => {
    if (!isOpen || !transaction) return null;

    return (
        <div className="fixed inset-0 z-50 overflow-hidden" aria-labelledby="slide-over-title" role="dialog" aria-modal="true">
            <div className="absolute inset-0 overflow-hidden">
                {/* Backdrop */}
                <div
                    className="absolute inset-0 bg-slate-900/75 transition-opacity"
                    onClick={onClose}
                    aria-hidden="true"
                />

                <div className="pointer-events-none fixed inset-y-0 right-0 flex max-w-full pl-10 sm:pl-16">
                    <div className="pointer-events-auto w-screen max-w-2xl transform transition-transform duration-500 ease-in-out sm:duration-700">
                        <div className="flex h-full flex-col overflow-y-scroll bg-white shadow-xl">

                            {/* Header */}
                            <div className="px-4 py-6 sm:px-6 border-b border-slate-200 bg-slate-50">
                                <div className="flex items-start justify-between">
                                    <div>
                                        <h2 className="text-lg font-semibold text-slate-900" id="slide-over-title">
                                            Transaction Details
                                        </h2>
                                        <p className="text-sm text-slate-500 mt-1">
                                            ID: {transaction.id.toUpperCase()}
                                        </p>
                                    </div>
                                    <div className="ml-3 flex h-7 items-center">
                                        <button
                                            type="button"
                                            className="rounded-md bg-white text-slate-400 hover:text-slate-500 focus:ring-2 focus:ring-blue-500 focus:outline-none"
                                            onClick={onClose}
                                        >
                                            <span className="sr-only">Close panel</span>
                                            <X size={24} />
                                        </button>
                                    </div>
                                </div>
                            </div>

                            {/* Body */}
                            <div className="relative flex-1 px-4 py-6 sm:px-6">
                                <div className="grid grid-cols-1 gap-8 md:grid-cols-2 h-full">

                                    {/* Left Column: Receipt Image */}
                                    <div className="flex flex-col h-full">
                                        <h3 className="text-sm font-medium text-slate-900 mb-3">Original Receipt</h3>
                                        <div className="flex-1 rounded-lg border border-slate-200 bg-slate-100 overflow-hidden flex items-center justify-center relative">
                                            {transaction.receiptUrl ? (
                                                <>
                                                    <img
                                                        src={transaction.receiptUrl}
                                                        alt="Receipt"
                                                        className="object-contain max-h-full w-full"
                                                        onError={(e: any) => {
                                                            e.target.style.display = 'none';
                                                            e.target.nextSibling.style.display = 'flex';
                                                        }}
                                                    />
                                                    <div className="hidden flex-col items-center justify-center p-4 text-center text-slate-500">
                                                        <svg className="w-12 h-12 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                                                        </svg>
                                                        <p className="text-sm">Failed to load receipt image</p>
                                                    </div>
                                                    {transaction.receiptUrl && (
                                                        <div className="absolute bottom-4 right-4 bg-black/70 text-white text-xs px-2 py-1 rounded">
                                                            Page 1 of 1
                                                        </div>
                                                    )}
                                                </>
                                            ) : (
                                                <div className="flex flex-col items-center justify-center p-4 text-center text-slate-500">
                                                    <svg className="w-12 h-12 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                                                    </svg>
                                                    <p className="text-sm">No receipt image available</p>
                                                </div>
                                            )}
                                        </div>
                                    </div>

                                    {/* Right Column: AI Analysis */}
                                    <div className="flex flex-col space-y-6">
                                        <div>
                                            <h3 className="text-sm font-medium text-slate-900 mb-3 flex items-center gap-2">
                                                <BrainCircuit size={18} className="text-blue-600" />
                                                AI Extraction
                                            </h3>

                                            <div className="bg-slate-50 rounded-lg p-4 border border-slate-100 space-y-4">
                                                <div>
                                                    <label className="block text-xs font-medium text-slate-500 uppercase">Merchant</label>
                                                    <p className="text-sm font-medium text-slate-900 mt-1">{transaction.merchant}</p>
                                                </div>

                                                <div className="grid grid-cols-2 gap-4">
                                                    <div>
                                                        <label className="block text-xs font-medium text-slate-500 uppercase">Date</label>
                                                        <p className="text-sm font-medium text-slate-900 mt-1">{transaction.date}</p>
                                                    </div>
                                                    <div>
                                                        <label className="block text-xs font-medium text-slate-500 uppercase">Total Amount</label>
                                                        <p className="text-lg font-bold text-slate-900 mt-1">฿{transaction.amount.toLocaleString()}</p>
                                                    </div>
                                                </div>

                                                <div>
                                                    <label className="block text-xs font-medium text-slate-500 uppercase">Tax ID</label>
                                                    <p className="text-sm font-mono text-slate-700 mt-1">{transaction.taxId || "Not found"}</p>
                                                </div>
                                            </div>
                                        </div>

                                        <div>
                                            <h3 className="text-sm font-medium text-slate-900 mb-3">Analysis Result</h3>
                                            <div className={clsx(
                                                "rounded-lg p-4 border",
                                                transaction.status === 'Verified' ? "bg-emerald-50 border-emerald-100" :
                                                    transaction.status === 'Needs Review' ? "bg-amber-50 border-amber-100" :
                                                        "bg-slate-50 border-slate-100"
                                            )}>
                                                <div className="flex items-start gap-3">
                                                    <CheckCircle size={20} className={clsx(
                                                        transaction.status === 'Verified' ? "text-emerald-600" : "text-amber-600"
                                                    )} />
                                                    <div>
                                                        <p className="text-sm font-semibold text-slate-900 mb-1">
                                                            Category: {transaction.category}
                                                        </p>
                                                        <p className="text-sm text-slate-600 leading-relaxed">
                                                            {transaction.aiReasoning}
                                                        </p>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>

                                        <div className="pt-4 mt-auto border-t border-slate-100">
                                            <div className="flex gap-3">
                                                <button className="flex-1 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors">
                                                    Confirm & Save
                                                </button>
                                                <button className="px-4 py-2 border border-slate-300 hover:bg-slate-50 text-slate-700 rounded-lg text-sm font-medium transition-colors">
                                                    Edit Details
                                                </button>
                                            </div>
                                        </div>

                                    </div>
                                </div>
                            </div>

                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default TransactionModal;
