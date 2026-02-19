import React, { useState, useEffect } from 'react';
import SummaryCards from '../components/Dashboard/SummaryCards';
import UploadZone from '../components/Dashboard/UploadZone';
import TransactionsTable from '../components/Dashboard/TransactionsTable';
import TransactionModal from '../components/Features/TransactionModal';
import { Transaction, SummaryStat } from '../data/mockData';
import { dashboardApi } from '../api/dashboard';
import { storage } from '../lib/storage';
import type { DashboardSummary, CategoryBreakdown } from '../types/dashboard';

const DashboardPage: React.FC = () => {
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [selectedTransaction, setSelectedTransaction] = useState<Transaction | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [isRefreshing, setIsRefreshing] = useState(false);
    const [error, setError] = useState<string>('');
    const [summaryData, setSummaryData] = useState<DashboardSummary | null>(null);

    useEffect(() => {
        fetchDashboardData();
    }, []);

    const fetchDashboardData = async (silent = false) => {
        if (silent) {
            setIsRefreshing(true);
        } else {
            setIsLoading(true);
        }
        setError('');

        try {
            const userId = storage.getUserId();
            const token = storage.getToken();
            
            console.log('=== Dashboard Data Fetch Debug ===');
            console.log('User ID from storage:', userId);
            console.log('User ID length:', userId?.length);
            console.log('Has token:', !!token);
            
            if (!userId) {
                console.error('ERROR: No user ID found in storage');
                setError('User not logged in');
                setIsLoading(false);
                return;
            }

            console.log('Calling API with userId:', userId);
            const response = await dashboardApi.getSummary(userId);
            
            console.log('SUCCESS: Dashboard API response:', response);
            console.log('Response success:', response.success);
            console.log('Response data:', response.data);
            
            if (response.data) {
                console.log('Total deductible:', response.data.total_deductible);
                console.log('Total transactions:', response.data.total_transactions);
                console.log('Recent transactions count:', response.data.recent_transactions?.length);
                console.log('Recent transactions:', response.data.recent_transactions);
            }
            
            if (response.success) {
                setSummaryData(response.data);
                
                if (response.data.total_transactions === 0) {
                    console.warn('WARNING: No transactions found for this user');
                }
            }
        } catch (err: any) {
            console.error('ERROR: Failed to fetch dashboard data:', err);
            console.error('Error details:', err.response?.data || err.message);
            setError(err?.message || 'Failed to load dashboard data');
        } finally {
            setIsLoading(false);
            setIsRefreshing(false);
        }
    };

    const mapToSummaryStats = (): SummaryStat[] => {
        if (!summaryData) {
            return [
                {
                    label: 'Total Deductions',
                    value: '฿ 0',
                    subValue: 'No transactions yet',
                    trend: 'neutral' as const,
                    color: 'blue' as const,
                },
                {
                    label: 'SSF/RMF Allowance',
                    value: '฿ 0',
                    subValue: 'No data available',
                    color: 'green' as const,
                },
                {
                    label: 'Documents Processed',
                    value: '0',
                    subValue: 'Start uploading receipts',
                    trend: 'neutral' as const,
                    color: 'slate' as const,
                },
            ];
        }

        return [
            {
                label: 'Total Deductions',
                value: `฿ ${summaryData.total_deductible_amount.toLocaleString()}`,
                subValue: `${summaryData.status_breakdown.verified} verified transactions`,
                trend: 'neutral' as const,
                color: 'blue' as const,
            },
            {
                label: 'SSF/RMF Allowance',
                value: getSsfRmfValue(),
                subValue: getSsfRmfSubValue(),
                color: 'green' as const,
            },
            {
                label: 'Documents Processed',
                value: summaryData.total_transactions.toString(),
                subValue: `${summaryData.status_breakdown.verified} verified`,
                trend: 'neutral' as const,
                color: 'slate' as const,
            },
        ];
    };

    const getSsfRmfValue = (): string => {
        if (!summaryData) return '฿ 0';
        
        const ssfRmfCategory = summaryData.category_breakdown['SSF/RMF'] || 
                              summaryData.category_breakdown['SSF'] ||
                              summaryData.category_breakdown['RMF'];
        
        if (ssfRmfCategory) {
            return `฿ ${ssfRmfCategory.total_deductible.toLocaleString()}`;
        }
        
        return '฿ 0';
    };

    const getSsfRmfSubValue = (): string => {
        if (!summaryData) return 'No limit set';
        
        const ssfRmfCategory = summaryData.category_breakdown['SSF/RMF'] || 
                              summaryData.category_breakdown['SSF'] ||
                              summaryData.category_breakdown['RMF'];
        
        if (ssfRmfCategory) {
            return `Remaining of ${ssfRmfCategory.max_limit.toLocaleString()}k limit`;
        }
        
        return 'No limit set';
    };

    const mapToTransactions = (): Transaction[] => {
        if (!summaryData) return [];

        const API_BASE_URL = 'http://localhost:8000';

        return summaryData.recent_transactions.map((tx) => ({
            id: tx.id,
            date: tx.transaction_date,
            merchant: tx.merchant_name,
            category: tx.category || 'Other',
            amount: tx.total_amount,
            status: mapStatus(tx.status),
            receiptUrl: tx.receipt_image_url ? `${API_BASE_URL}${tx.receipt_image_url}` : '',
            aiReasoning: '',
        }));
    };

    const mapStatus = (status: string): 'Verified' | 'Processing' | 'Needs Review' => {
        if (status === 'verified') return 'Verified';
        if (status === 'rejected') return 'Needs Review';
        return 'Processing';
    };

    const getCategoryBreakdownArray = (): Array<{name: string; used: number; limit: number; percentage: number}> => {
        if (!summaryData) return [];

        return Object.entries(summaryData.category_breakdown).map(([name, data]) => ({
            name,
            used: data.total_deductible,
            limit: data.max_limit,
            percentage: (data.total_deductible / data.max_limit) * 100,
        }));
    };

    const handleTransactionClick = (transaction: Transaction) => {
        setSelectedTransaction(transaction);
        setIsModalOpen(true);
    };

    const handleCloseModal = () => {
        setIsModalOpen(false);
        setTimeout(() => setSelectedTransaction(null), 300);
    };

    if (isLoading) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
                    <p className="text-slate-600">Loading dashboard...</p>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="space-y-6">
                <div>
                    <h2 className="text-2xl font-bold text-slate-900">Dashboard</h2>
                    <p className="text-slate-500 mt-1">Overview of your tax deductions and uploaded documents.</p>
                </div>
                <div className="bg-red-50 border border-red-200 rounded-lg p-6">
                    <div className="flex items-start">
                        <div className="flex-shrink-0">
                            <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                            </svg>
                        </div>
                        <div className="ml-3">
                            <h3 className="text-sm font-medium text-red-800">Error loading dashboard</h3>
                            <p className="mt-2 text-sm text-red-700">{error}</p>
                            <div className="mt-4">
                                <button 
                                    onClick={fetchDashboardData}
                                    className="px-4 py-2 bg-red-100 text-red-800 text-sm font-medium rounded-lg hover:bg-red-200 transition-colors"
                                >
                                    Try again
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            {/* Header Section of the Page */}
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-2xl font-bold text-slate-900">Dashboard</h2>
                    <p className="text-slate-500 mt-1">Overview of your tax deductions and uploaded documents.</p>
                </div>
                <button
                    onClick={() => fetchDashboardData(true)}
                    disabled={isRefreshing}
                    className="flex items-center gap-2 px-4 py-2 bg-primary-600 text-white font-medium rounded-lg hover:bg-primary-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                    <svg 
                        className={`w-4 h-4 ${isRefreshing ? 'animate-spin' : ''}`}
                        fill="none" 
                        stroke="currentColor" 
                        viewBox="0 0 24 24"
                    >
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                    </svg>
                    {isRefreshing ? 'Refreshing...' : 'Refresh'}
                </button>
            </div>

            <SummaryCards stats={mapToSummaryStats()} />

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Main Content Area */}
                <div className="lg:col-span-2 space-y-8">
                    <section>
                        <h3 className="text-lg font-semibold text-slate-900 mb-4">Quick Upload</h3>
                        <UploadZone onUploadSuccess={() => fetchDashboardData(true)} />
                    </section>

                    <section>
                        <TransactionsTable
                            transactions={mapToTransactions()}
                            onSelectTransaction={handleTransactionClick}
                        />
                    </section>
                </div>

                {/* Side Widget Area */}
                <div className="space-y-6">
                    <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200">
                        <h3 className="font-semibold text-slate-900 mb-4">Deduction Limits</h3>

                        <div className="space-y-4">
                            {getCategoryBreakdownArray().slice(0, 3).map((category) => (
                                <div key={category.name}>
                                    <div className="flex justify-between text-sm mb-1">
                                        <span className="text-slate-600">{category.name}</span>
                                        <span className="font-medium text-slate-900">
                                            {Math.round(category.percentage)}%
                                        </span>
                                    </div>
                                    <div className="h-2 bg-slate-100 rounded-full overflow-hidden">
                                        <div 
                                            className="h-full bg-primary-500 rounded-full"
                                            style={{ width: `${Math.min(category.percentage, 100)}%` }}
                                        ></div>
                                    </div>
                                    <p className="text-xs text-slate-400 mt-1">
                                        ฿{category.used.toLocaleString()} used of ฿{category.limit.toLocaleString()}
                                    </p>
                                </div>
                            ))}

                            {getCategoryBreakdownArray().length === 0 && (
                                <p className="text-sm text-slate-500 text-center py-4">
                                    No deduction data available
                                </p>
                            )}
                        </div>

                        <button className="w-full mt-6 py-2 text-sm text-primary-600 font-medium border border-primary-100 hover:bg-primary-50 rounded-lg transition-colors">
                            View Detailed Rules
                        </button>
                    </div>
                </div>
            </div>

            <TransactionModal
                isOpen={isModalOpen}
                transaction={selectedTransaction}
                onClose={handleCloseModal}
            />
        </div>
    );
};

export default DashboardPage;
