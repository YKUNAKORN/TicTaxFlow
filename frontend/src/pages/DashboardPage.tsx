import React, { useState } from 'react';
import SummaryCards from '../components/Dashboard/SummaryCards';
import UploadZone from '../components/Dashboard/UploadZone';
import TransactionsTable from '../components/Dashboard/TransactionsTable';
import TransactionModal from '../components/Features/TransactionModal';
import { mockSummaryStats, mockTransactions, Transaction } from '../data/mockData';

const DashboardPage: React.FC = () => {
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [selectedTransaction, setSelectedTransaction] = useState<Transaction | null>(null);

    const handleTransactionClick = (transaction: Transaction) => {
        setSelectedTransaction(transaction);
        setIsModalOpen(true);
    };

    const handleCloseModal = () => {
        setIsModalOpen(false);
        setTimeout(() => setSelectedTransaction(null), 300);
    };

    return (
        <div className="space-y-6">
            {/* Header Section of the Page */}
            <div>
                <h2 className="text-2xl font-bold text-slate-900">Dashboard</h2>
                <p className="text-slate-500 mt-1">Overview of your tax deductions and uploaded documents.</p>
            </div>

            <SummaryCards stats={mockSummaryStats} />

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Main Content Area */}
                <div className="lg:col-span-2 space-y-8">
                    <section>
                        <h3 className="text-lg font-semibold text-slate-900 mb-4">Quick Upload</h3>
                        <UploadZone />
                    </section>

                    <section>
                        <TransactionsTable
                            transactions={mockTransactions}
                            onSelectTransaction={handleTransactionClick}
                        />
                    </section>
                </div>

                {/* Side Widget Area */}
                <div className="space-y-6">
                    <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200">
                        <h3 className="font-semibold text-slate-900 mb-4">Deduction Limits</h3>

                        <div className="space-y-4">
                            <div>
                                <div className="flex justify-between text-sm mb-1">
                                    <span className="text-slate-600">SSF/RMF</span>
                                    <span className="font-medium text-slate-900">77%</span>
                                </div>
                                <div className="h-2 bg-slate-100 rounded-full overflow-hidden">
                                    <div className="h-full bg-primary-500 w-[77%] rounded-full"></div>
                                </div>
                                <p className="text-xs text-slate-400 mt-1">฿154,800 used of ฿200,000</p>
                            </div>

                            <div>
                                <div className="flex justify-between text-sm mb-1">
                                    <span className="text-slate-600">Life Insurance</span>
                                    <span className="font-medium text-slate-900">45%</span>
                                </div>
                                <div className="h-2 bg-slate-100 rounded-full overflow-hidden">
                                    <div className="h-full bg-secondary-500 w-[45%] rounded-full"></div>
                                </div>
                                <p className="text-xs text-slate-400 mt-1">฿45,000 used of ฿100,000</p>
                            </div>

                            <div>
                                <div className="flex justify-between text-sm mb-1">
                                    <span className="text-slate-600">Easy E-Receipt</span>
                                    <span className="font-medium text-slate-900">12%</span>
                                </div>
                                <div className="h-2 bg-slate-100 rounded-full overflow-hidden">
                                    <div className="h-full bg-accent-500 w-[12%] rounded-full"></div>
                                </div>
                                <p className="text-xs text-slate-400 mt-1">฿6,000 used of ฿50,000</p>
                            </div>
                        </div>

                        <button className="w-full mt-6 py-2 text-sm text-primary-600 font-medium border border-primary-100 hover:bg-primary-50 rounded-lg transition-colors">
                            View Detailed Rules
                        </button>
                    </div>

                    {/* <div className="bg-slate-900 p-6 rounded-xl shadow-md text-white border border-slate-800">
                        <h3 className="font-bold text-lg mb-2">Need Help?</h3>
                        <p className="text-slate-300 text-sm mb-4">Ask our AI Tax Assistant about specific deduction rules or regulations.</p>
                        <button className="w-full py-2 bg-white/10 hover:bg-white/20 text-white rounded-lg text-sm font-medium transition-colors backdrop-blur-sm">
                            Chat with AI Agent
                        </button>
                    </div> */}
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
