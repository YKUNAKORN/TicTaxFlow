import React from 'react';
import { Transaction } from '../../data/mockData';
import { MoreHorizontal, FileCheck, Clock, AlertCircle } from 'lucide-react';
import { clsx } from 'clsx';

interface TransactionsTableProps {
    transactions: Transaction[];
    onSelectTransaction: (transaction: Transaction) => void;
}

const TransactionsTable: React.FC<TransactionsTableProps> = ({ transactions, onSelectTransaction }) => {
    const getStatusBadge = (status: string) => {
        switch (status) {
            case 'Verified':
                return (
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-emerald-100 text-emerald-800">
                        <FileCheck size={14} className="mr-1" /> Verified
                    </span>
                );
            case 'Processing':
                return (
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-amber-100 text-amber-800">
                        <Clock size={14} className="mr-1" /> Processing
                    </span>
                );
            case 'Needs Review':
                return (
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-amber-100 text-amber-800">
                        <AlertCircle size={14} className="mr-1" /> Needs Review
                    </span>
                );
            case 'Not Deductible':
                return (
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                        <AlertCircle size={14} className="mr-1" /> Not Deductible
                    </span>
                );
            default:
                return null;
        }
    };

    return (
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
            <div className="px-6 py-4 border-b border-slate-200 flex justify-between items-center">
                <h3 className="font-semibold text-slate-900">Recent Transactions</h3>
                <button className="text-sm text-blue-600 hover:text-blue-800 font-medium">View All</button>
            </div>
            <div className="overflow-x-auto">
                <table className="w-full text-left text-sm text-slate-600">
                    <thead className="bg-slate-50 text-xs uppercase text-slate-500 font-semibold">
                        <tr>
                            <th className="px-6 py-4">Date</th>
                            <th className="px-6 py-4">Merchant</th>
                            <th className="px-6 py-4">Category</th>
                            <th className="px-6 py-4 text-right">Amount</th>
                            <th className="px-6 py-4">Status</th>
                            <th className="px-6 py-4"></th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-200">
                        {transactions.length === 0 ? (
                            <tr>
                                <td colSpan={6} className="px-6 py-12 text-center">
                                    <div className="flex flex-col items-center justify-center text-slate-400">
                                        <FileCheck size={48} className="mb-3 opacity-30" />
                                        <p className="text-sm font-medium text-slate-600">No transactions yet</p>
                                        <p className="text-xs mt-1">Upload a receipt to get started</p>
                                    </div>
                                </td>
                            </tr>
                        ) : (
                            transactions.map((tx) => (
                                <tr
                                    key={tx.id}
                                    onClick={() => onSelectTransaction(tx)}
                                    className="hover:bg-slate-50 transition-colors cursor-pointer"
                                >
                                    <td className="px-6 py-4 whitespace-nowrap">{tx.date}</td>
                                    <td className="px-6 py-4 font-medium text-slate-900">{tx.merchant}</td>
                                    <td className="px-6 py-4">
                                        <span className="px-2 py-1 bg-slate-100 rounded text-slate-600 text-xs">
                                            {tx.category}
                                        </span>
                                    </td>
                                    <td className="px-6 py-4 text-right font-medium text-slate-900">
                                        ฿{tx.amount.toLocaleString()}
                                    </td>
                                    <td className="px-6 py-4">{getStatusBadge(tx.status)}</td>
                                    <td className="px-6 py-4 text-right">
                                        <button className="text-slate-400 hover:text-slate-600 p-1 rounded-full hover:bg-slate-100">
                                            <MoreHorizontal size={20} />
                                        </button>
                                    </td>
                                </tr>
                            ))
                        )}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

export default TransactionsTable;
