import React, { useState, useEffect } from 'react';
import { 
    Search, Filter, ArrowUpRight, ArrowDownLeft, Download, RefreshCw, 
    ChevronLeft, ChevronRight, FileText, CheckCircle, Clock, AlertCircle, MoreHorizontal 
} from 'lucide-react';
import { transactionsApi } from '../api';
import { storage } from '../lib/storage';

// Map backend status values to display labels
const STATUS_MAP: any = {
    verified: 'Verified',
    needs_review: 'Needs Review',
    rejected: 'Rejected',
    processing: 'Processing',
};

// Map display labels back to backend status values
const STATUS_FILTER_MAP: any = {
    'All': undefined,
    'Verified': 'verified',
    'Processing': 'processing',
    'Needs Review': 'needs_review',
};

const TransactionsPage: React.FC = () => {
    const [transactions, setTransactions] = useState<any[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [isRefreshing, setIsRefreshing] = useState(false);
    const [error, setError] = useState('');
    const [searchTerm, setSearchTerm] = useState('');
    const [statusFilter, setStatusFilter] = useState('All');
    const [currentPage, setCurrentPage] = useState(1);
    const [summaryData, setSummaryData] = useState<any>(null);
    const itemsPerPage = 7;

    useEffect(() => {
        fetchTransactions();
        fetchSummary();
    }, []);

    const fetchTransactions = async (silent = false) => {
        const userId = storage.getUserId();
        if (!userId) {
            setError('User not logged in');
            setIsLoading(false);
            return;
        }

        if (silent) {
            setIsRefreshing(true);
        } else {
            setIsLoading(true);
        }
        setError('');

        try {
            const response = await transactionsApi.getUserTransactions(userId);
            if (response.success) {
                setTransactions(response.transactions || []);
            }
        } catch (err: any) {
            console.error('Failed to fetch transactions:', err);
            setError(err?.message || 'Failed to load transactions');
        } finally {
            setIsLoading(false);
            setIsRefreshing(false);
        }
    };

    const fetchSummary = async () => {
        const userId = storage.getUserId();
        if (!userId) return;

        try {
            const response = await transactionsApi.getSummary(userId);
            if (response.success) {
                setSummaryData(response.data);
            }
        } catch (err: any) {
            console.error('Failed to fetch transaction summary:', err);
        }
    };

    const handleDeleteTransaction = async (transactionId: string) => {
        try {
            const response = await transactionsApi.deleteTransaction(transactionId);
            if (response.success) {
                // Refresh data after deletion
                fetchTransactions(true);
                fetchSummary();
            }
        } catch (err: any) {
            console.error('Failed to delete transaction:', err);
        }
    };

    // Filter transactions based on search and status
    const filteredTransactions = transactions.filter((tx: any) => {
        const merchant = tx.merchant_name || '';
        const category = tx.category_name || '';
        const matchesSearch = merchant.toLowerCase().includes(searchTerm.toLowerCase()) || 
                            category.toLowerCase().includes(searchTerm.toLowerCase());
        const displayStatus = STATUS_MAP[tx.status] || tx.status;
        const matchesStatus = statusFilter === 'All' || displayStatus === statusFilter;
        return matchesSearch && matchesStatus;
    });

    // Pagination logic
    const totalPages = Math.ceil(filteredTransactions.length / itemsPerPage);
    const startIndex = (currentPage - 1) * itemsPerPage;
    const currentTransactions = filteredTransactions.slice(startIndex, startIndex + itemsPerPage);

    // Calculate summary stats from API or fallback to local calculation
    const totalAmount = summaryData?.total_deductible_amount ?? filteredTransactions.reduce((sum: any, tx: any) => sum + (tx.total_amount || 0), 0);
    const verifiedCount = summaryData?.status_breakdown?.verified ?? filteredTransactions.filter((tx: any) => tx.status === 'verified').length;
    const pendingCount = summaryData?.status_breakdown?.needs_review ?? filteredTransactions.filter((tx: any) => tx.status === 'needs_review').length;

    // Calculate month-over-month change using the raw transactions list
    const now = new Date();
    const curMonth = now.getMonth();
    const curYear = now.getFullYear();
    const prevMonth = curMonth === 0 ? 11 : curMonth - 1;
    const prevYear = curMonth === 0 ? curYear - 1 : curYear;

    const currentMonthTotal = transactions
        .filter((tx) => {
            const d = new Date(tx.transaction_date);
            return d.getMonth() === curMonth && d.getFullYear() === curYear;
        })
        .reduce((sum: number, tx) => sum + (tx.total_amount || 0), 0);

    const prevMonthTotal = transactions
        .filter((tx) => {
            const d = new Date(tx.transaction_date);
            return d.getMonth() === prevMonth && d.getFullYear() === prevYear;
        })
        .reduce((sum: number, tx) => sum + (tx.total_amount || 0), 0);

    const monthChangePercent: number | null =
        prevMonthTotal > 0
            ? ((currentMonthTotal - prevMonthTotal) / prevMonthTotal) * 100
            : null;

    const getStatusColor = (status: string) => {
        switch (status) {
            case 'Verified': return 'bg-emerald-100 text-emerald-700 border-emerald-200';
            case 'Processing': return 'bg-blue-100 text-blue-700 border-blue-200';
            case 'Needs Review': return 'bg-amber-100 text-amber-700 border-amber-200';
            default: return 'bg-slate-100 text-slate-700 border-slate-200';
        }
    };

    const getStatusIcon = (status: string) => {
        switch (status) {
            case 'Verified': return <CheckCircle size={14} className="mr-1.5" />;
            case 'Processing': return <Clock size={14} className="mr-1.5" />;
            case 'Needs Review': return <AlertCircle size={14} className="mr-1.5" />;
            default: return null;
        }
    };

    // Show loading spinner on initial load
    if (isLoading) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
                    <p className="text-slate-600">Loading transactions...</p>
                </div>
            </div>
        );
    }

    // Show error state
    if (error) {
        return (
            <div className="space-y-6">
                <div>
                    <h2 className="text-2xl font-bold text-slate-900">Transaction History</h2>
                    <p className="text-slate-500 mt-1">Manage and track all your tax-deductible expenses.</p>
                </div>
                <div className="bg-red-50 border border-red-200 rounded-lg p-6">
                    <div className="flex items-start">
                        <AlertCircle className="h-5 w-5 text-red-400 flex-shrink-0 mt-0.5" />
                        <div className="ml-3">
                            <h3 className="text-sm font-medium text-red-800">Error loading transactions</h3>
                            <p className="mt-2 text-sm text-red-700">{error}</p>
                            <button 
                                onClick={() => fetchTransactions()}
                                className="mt-4 px-4 py-2 bg-red-100 text-red-800 text-sm font-medium rounded-lg hover:bg-red-200 transition-colors"
                            >
                                Try again
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            {/* Page Header */}
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                    <h1 className="text-2xl font-bold text-slate-900">Transaction History</h1>
                    <p className="text-slate-500 mt-1">Manage and track all your tax-deductible expenses.</p>
                </div>
                <div className="flex items-center gap-3">
                    <button className="flex items-center gap-2 px-4 py-2 bg-white border border-slate-200 rounded-lg text-slate-600 hover:bg-slate-50 hover:text-slate-900 transition-colors shadow-sm">
                        <Download size={18} />
                        <span className="font-medium">Export CSV</span>
                    </button>
                    <button 
                        onClick={() => { fetchTransactions(true); fetchSummary(); }}
                        disabled={isRefreshing}
                        className="flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors shadow-md shadow-primary-200 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        <RefreshCw size={18} className={isRefreshing ? 'animate-spin' : ''} />
                        <span className="font-medium">{isRefreshing ? 'Syncing...' : 'Sync Data'}</span>
                    </button>
                </div>
            </div>

            {/* Summary Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm relative overflow-hidden group">
                    <div className="relative z-10">
                        <p className="text-sm font-medium text-slate-500 uppercase tracking-wider">Total Expenses</p>
                        <h3 className="text-3xl font-bold text-slate-900 mt-2">฿{totalAmount.toLocaleString()}</h3>
                        <div
                            className={`flex items-center mt-4 text-sm font-medium w-fit px-2 py-1 rounded-full ${
                                monthChangePercent === null
                                    ? 'bg-slate-100 text-slate-500'
                                    : monthChangePercent >= 0
                                    ? 'bg-emerald-50 text-emerald-600'
                                    : 'bg-red-50 text-red-500'
                            }`}
                        >
                            {monthChangePercent !== null ? (
                                monthChangePercent >= 0 ? (
                                    <ArrowUpRight size={14} className="mr-1" />
                                ) : (
                                    <ArrowDownLeft size={14} className="mr-1" />
                                )
                            ) : null}
                            <span>
                                {monthChangePercent !== null
                                    ? `${monthChangePercent >= 0 ? '+' : ''}${monthChangePercent.toFixed(1)}% from last month`
                                    : 'No data from last month'}
                            </span>
                        </div>
                    </div>
                </div>

                <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm relative overflow-hidden group">
                    <div className="relative z-10">
                        <p className="text-sm font-medium text-slate-500 uppercase tracking-wider">Verified Items</p>
                        <h3 className="text-3xl font-bold text-slate-900 mt-2">{verifiedCount}</h3>
                        <p className="text-slate-400 text-sm mt-4">Ready for tax filing</p>
                    </div>
                </div>

                <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm relative overflow-hidden group">
                    <div className="relative z-10">
                        <p className="text-sm font-medium text-slate-500 uppercase tracking-wider">Pending Review</p>
                        <h3 className="text-3xl font-bold text-slate-900 mt-2">{pendingCount}</h3>
                        <p className="text-slate-400 text-sm mt-4">Awaiting AI verification</p>
                    </div>
                </div>
            </div>

            {/* Main Content Area */}
            <div className="bg-white rounded-xl shadow-sm border border-slate-200 flex flex-col min-h-[500px]">
                {/* Toolbar */}
                <div className="p-5 border-b border-slate-200 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                    {/* Search */}
                    <div className="relative max-w-md w-full">
                        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                            <Search className="h-4 w-4 text-slate-400" />
                        </div>
                        <input
                            type="text"
                            className="block w-full pl-10 pr-3 py-2 border border-slate-200 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent text-sm bg-slate-50 hover:bg-white transition-colors"
                            placeholder="Search by merchant or category..."
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                        />
                    </div>

                    {/* Filter Tabs */}
                    <div className="flex items-center gap-2 overflow-x-auto pb-2 sm:pb-0">
                        {['All', 'Verified', 'Processing', 'Needs Review'].map((status) => (
                            <button
                                key={status}
                                onClick={() => setStatusFilter(status)}
                                className={`px-4 py-1.5 text-sm font-medium rounded-full transition-all whitespace-nowrap ${
                                    statusFilter === status
                                        ? 'bg-primary-600 text-white shadow-md'
                                        : 'bg-slate-100 text-slate-600 hover:bg-slate-200 hover:text-slate-900'
                                }`}
                            >
                                {status}
                            </button>
                        ))}
                    </div>
                </div>

                {/* Table */}
                <div className="overflow-x-auto flex-1">
                    <table className="w-full text-left border-collapse">
                        <thead>
                            <tr className="bg-slate-50 border-b border-slate-200">
                                <th className="px-6 py-4 text-xs font-semibold text-slate-500 uppercase tracking-wider">Date</th>
                                <th className="px-6 py-4 text-xs font-semibold text-slate-500 uppercase tracking-wider">Merchant / Transaction ID</th>
                                <th className="px-6 py-4 text-xs font-semibold text-slate-500 uppercase tracking-wider">Category</th>
                                <th className="px-6 py-4 text-xs font-semibold text-slate-500 uppercase tracking-wider text-right">Amount</th>
                                <th className="px-6 py-4 text-xs font-semibold text-slate-500 uppercase tracking-wider">Status</th>
                                <th className="px-6 py-4 text-xs font-semibold text-slate-500 uppercase tracking-wider text-right">Actions</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-100">
                            {currentTransactions.length > 0 ? (
                                currentTransactions.map((tx: any) => (
                                    <tr key={tx.id} className="group hover:bg-slate-50 transition-colors cursor-pointer">
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-600">
                                            {tx.transaction_date ? new Date(tx.transaction_date).toLocaleDateString('en-US', { 
                                                year: 'numeric', 
                                                month: 'short', 
                                                day: 'numeric' 
                                            }) : '-'}
                                        </td>
                                        <td className="px-6 py-4">
                                            <div className="flex items-center">
                                                <div className="h-8 w-8 rounded-full bg-primary-50 flex items-center justify-center text-primary-600 mr-3 group-hover:bg-primary-100 transition-colors">
                                                    <FileText size={16} />
                                                </div>
                                                <div>
                                                    <div className="font-medium text-slate-900">{tx.merchant_name || 'Unknown Merchant'}</div>
                                                    <div className="text-xs text-slate-400 font-mono mt-0.5">{tx.id?.slice(0, 8)}...</div>
                                                </div>
                                            </div>
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-slate-100 text-slate-700 border border-slate-200">
                                                {tx.category_name || 'Uncategorized'}
                                            </span>
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-semibold text-slate-900">
                                            ฿{(tx.total_amount || 0).toLocaleString()}
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium border ${getStatusColor(STATUS_MAP[tx.status] || tx.status)}`}>
                                                {getStatusIcon(STATUS_MAP[tx.status] || tx.status)}
                                                {STATUS_MAP[tx.status] || tx.status}
                                            </span>
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                                            <button 
                                                onClick={(e) => { e.stopPropagation(); handleDeleteTransaction(tx.id); }}
                                                className="p-1.5 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded-full transition-colors"
                                                title="Delete transaction"
                                            >
                                                <MoreHorizontal size={18} />
                                            </button>
                                        </td>
                                    </tr>
                                ))
                            ) : (
                                <tr>
                                    <td colSpan={6} className="px-6 py-24 text-center">
                                        <div className="flex flex-col items-center justify-center">
                                            <div className="h-16 w-16 bg-slate-50 rounded-full flex items-center justify-center mb-4">
                                                <Search size={32} className="text-slate-300" />
                                            </div>
                                            <h3 className="text-lg font-medium text-slate-900 mb-1">No transactions found</h3>
                                            <p className="text-slate-500 max-w-xs mx-auto">
                                                We couldn't find any transactions matching your search criteria.
                                            </p>
                                            <button 
                                                onClick={() => {setSearchTerm(''); setStatusFilter('All');}}
                                                className="mt-4 text-primary-600 hover:text-primary-700 font-medium text-sm"
                                            >
                                                Clear all filters
                                            </button>
                                        </div>
                                    </td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>

                {/* Pagination Footer */}
                <div className="px-6 py-4 border-t border-slate-200 flex items-center justify-between bg-slate-50 rounded-b-xl">
                    <p className="text-sm text-slate-500">
                        Showing <span className="font-medium text-slate-900">{filteredTransactions.length > 0 ? startIndex + 1 : 0}</span> to <span className="font-medium text-slate-900">{Math.min(startIndex + itemsPerPage, filteredTransactions.length)}</span> of <span className="font-medium text-slate-900">{filteredTransactions.length}</span> results
                    </p>
                    <div className="flex items-center gap-2">
                        <button
                            onClick={() => setCurrentPage(prev => Math.max(prev - 1, 1))}
                            disabled={currentPage === 1}
                            className="p-2 border border-slate-200 rounded-lg bg-white text-slate-600 hover:bg-slate-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                        >
                            <ChevronLeft size={16} />
                        </button>
                        <span className="text-sm font-medium text-slate-700 px-2">Page {currentPage} of {totalPages || 1}</span>
                        <button
                            onClick={() => setCurrentPage(prev => Math.min(prev + 1, totalPages))}
                            disabled={currentPage === totalPages || totalPages === 0}
                            className="p-2 border border-slate-200 rounded-lg bg-white text-slate-600 hover:bg-slate-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                        >
                            <ChevronRight size={16} />
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default TransactionsPage;
