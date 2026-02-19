import React from 'react';
import { Link } from 'react-router-dom';
import { CheckCircle, Shield, Zap, BookOpen, PieChart, FileText, Bot } from 'lucide-react';
import logo from '../assets/logo-icon.png';

const FeaturesPage: React.FC = () => {
    return (
        <div className="min-h-screen bg-white">
            {/* Navbar */}
            <nav className="flex items-center justify-between px-6 py-4 max-w-7xl mx-auto">
                <div className="flex items-center gap-2">
                    <Link to="/">
                        <img src={logo} alt="Logo" className="h-10 w-auto" />
                    </Link>
                    <Link to="/" className="text-xl font-bold text-slate-900">TicTaxFlow</Link>
                </div>
                <div className="hidden md:flex items-center gap-8">
                    <Link to="/" className="text-sm font-medium text-slate-600 hover:text-slate-900 transition-colors">Home</Link>
                    <Link to="/features" className="text-sm font-medium text-slate-900 transition-colors">Features</Link>
                    <Link to="/about" className="text-sm font-medium text-slate-600 hover:text-slate-900 transition-colors">About</Link>
                </div>
                <div className="flex items-center gap-4">
                    <Link to="/signin" className="text-sm font-medium text-slate-600 hover:text-slate-900">Login</Link>
                    <Link to="/signup" className="px-4 py-2 bg-slate-900 text-white text-sm font-medium rounded-lg hover:bg-slate-800 transition-colors">
                        Get Started
                    </Link>
                </div>
            </nav>

            <main className="max-w-7xl mx-auto px-6 py-12 lg:py-20 animate-fade-in-up">
                <div className="text-center mb-24">
                    <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary-50 text-primary-600 text-sm font-medium border border-primary-100 mb-6">
                        <span className="relative flex h-2 w-2">
                            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-primary-400 opacity-75"></span>
                            <span className="relative inline-flex rounded-full h-2 w-2 bg-primary-500"></span>
                        </span>
                        Powerful Features v2.0
                    </div>
                    <h1 className="text-4xl lg:text-6xl font-bold text-slate-900 mb-6 tracking-tight">
                        Everything you need for <br/>
                        <span className="text-primary-600">smarter tax planning</span>
                    </h1>
                    <p className="text-slate-500 text-lg max-w-2xl mx-auto leading-relaxed">
                        TicTaxFlow combines computer vision, natural language processing, and regulatory databases to automate your entire tax workflow from receipt to filing.
                    </p>
                </div>

                {/* Feature Deep Dive 1: Extraction */}
                <div className="flex flex-col lg:flex-row items-center gap-16 mb-32">
                    <div className="flex-1 space-y-6">
                        <div className="h-14 w-14 bg-primary-50 rounded-2xl flex items-center justify-center text-primary-600">
                            <Bot size={28} />
                        </div>
                        <h2 className="text-3xl font-bold text-slate-900">AI-Powered Receipt Analysis</h2>
                        <p className="text-slate-500 text-lg leading-relaxed">
                            Stop typing details manually. Our advanced OCR engine instantly extracts merchant names, tax IDs, dates, and total amounts from photos or PDFs of your receipts.
                        </p>
                        <ul className="space-y-4">
                            {[
                                'Supports both e-Tax invoices and paper receipts',
                                'Automatic currency normalization',
                                'Duplicate detection to prevent double counting'
                            ].map((item, i) => (
                                <li key={i} className="flex items-center gap-3 text-slate-700">
                                    <div className="h-6 w-6 rounded-full bg-green-100 flex items-center justify-center text-green-600 flex-shrink-0">
                                        <CheckCircle size={14} />
                                    </div>
                                    {item}
                                </li>
                            ))}
                        </ul>
                    </div>
                    <div className="flex-1 relative">
                        <div className="absolute -inset-4 bg-gradient-to-r from-primary-600 to-purple-600 rounded-2xl opacity-20 blur-2xl"></div>
                        <div className="relative bg-white rounded-2xl border border-slate-200 shadow-xl p-8">
                            <div className="flex items-center gap-4 mb-6 border-b border-slate-100 pb-4">
                                <div className="h-3 w-3 rounded-full bg-red-400"></div>
                                <div className="h-3 w-3 rounded-full bg-yellow-400"></div>
                                <div className="h-3 w-3 rounded-full bg-green-400"></div>
                                <div className="ml-auto text-xs text-slate-400 font-mono">receipt_analysis.json</div>
                            </div>
                            <div className="space-y-4 font-mono text-sm">
                                <div className="flex justify-between">
                                    <span className="text-primary-600">"merchant":</span>
                                    <span className="text-slate-900">"7-Eleven"</span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-primary-600">"tax_id":</span>
                                    <span className="text-slate-900">"010553203..."</span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-primary-600">"amount":</span>
                                    <span className="text-slate-900">1,250.00THB</span>
                                </div>
                                <div className="flex justify-between items-center bg-green-50 p-2 rounded -mx-2">
                                    <span className="text-green-600">"confidence":</span>
                                    <span className="text-green-700 font-bold">99.8%</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Feature Deep Dive 2: Categorization */}
                <div className="flex flex-col lg:flex-row-reverse items-center gap-16 mb-32">
                    <div className="flex-1 space-y-6">
                        <div className="h-14 w-14 bg-secondary-50 rounded-2xl flex items-center justify-center text-secondary-600">
                            <Zap size={28} />
                        </div>
                        <h2 className="text-3xl font-bold text-slate-900">Intelligent Tax Categorization</h2>
                        <p className="text-slate-500 text-lg leading-relaxed">
                            Our AI understands the context of your spending. It automatically maps expenses to the correct Revenue Department tax allowance categories—like ESG, Easy E-Receipt, or Donation.
                        </p>
                        <p className="text-slate-500 text-lg leading-relaxed">
                            Never miss a deduction opportunity again. The system suggests the best category to maximize your tax refund.
                        </p>
                    </div>
                    <div className="flex-1 relative">
                        <div className="grid grid-cols-2 gap-4">
                            <div className="p-6 bg-white rounded-xl border border-slate-200 shadow-sm hover:border-secondary-200 transition-colors">
                                <div className="h-10 w-10 bg-blue-50 text-blue-600 rounded-lg flex items-center justify-center mb-3">
                                    <BookOpen size={20} />
                                </div>
                                <h4 className="font-semibold text-slate-900">Education</h4>
                                <p className="text-xs text-slate-500 mt-1">2x Deduction Eligible</p>
                            </div>
                            <div className="p-6 bg-white rounded-xl border border-secondary-200 shadow-md transform translate-y-4">
                                <div className="h-10 w-10 bg-secondary-50 text-secondary-600 rounded-lg flex items-center justify-center mb-3">
                                    <Zap size={20} />
                                </div>
                                <h4 className="font-semibold text-slate-900">Easy E-Receipt</h4>
                                <p className="text-xs text-slate-500 mt-1">Max 50,000 THB</p>
                            </div>
                            <div className="p-6 bg-white rounded-xl border border-slate-200 shadow-sm hover:border-secondary-200 transition-colors">
                                <div className="h-10 w-10 bg-green-50 text-green-600 rounded-lg flex items-center justify-center mb-3">
                                    <Shield size={20} />
                                </div>
                                <h4 className="font-semibold text-slate-900">Insurance</h4>
                                <p className="text-xs text-slate-500 mt-1">General & Health</p>
                            </div>
                            <div className="p-6 bg-white rounded-xl border border-slate-200 shadow-sm hover:border-secondary-200 transition-colors transform translate-y-4">
                                <div className="h-10 w-10 bg-orange-50 text-orange-600 rounded-lg flex items-center justify-center mb-3">
                                    <PieChart size={20} />
                                </div>
                                <h4 className="font-semibold text-slate-900">SSF / RMF</h4>
                                <p className="text-xs text-slate-500 mt-1">Investment Funds</p>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Feature Deep Dive 3: Compliance */}
                <div className="flex flex-col lg:flex-row items-center gap-16 mb-24">
                    <div className="flex-1 space-y-6">
                        <div className="h-14 w-14 bg-accent-50 rounded-2xl flex items-center justify-center text-accent-600">
                            <Shield size={28} />
                        </div>
                        <h2 className="text-3xl font-bold text-slate-900">Real-time Compliance Checks</h2>
                        <p className="text-slate-500 text-lg leading-relaxed">
                            Our "Inspector" agent verifies every transaction against current laws to ensure audit-readiness. It checks for validity, date ranges, and maximum deduction limits.
                        </p>
                        <div className="bg-slate-50 border border-slate-200 rounded-xl p-6">
                            <div className="flex items-start gap-4">
                                <div className="h-10 w-10 rounded-full bg-white border border-slate-200 flex items-center justify-center text-xl flex-shrink-0">
                                    👮
                                </div>
                                <div>
                                    <h4 className="font-semibold text-slate-900">The Inspector Says:</h4>
                                    <p className="text-slate-600 mt-2 text-sm italic">
                                        "Warning: You have exceeded the 100,000 THB limit for General Life Insurance. The excess amount of 25,000 THB will not be calculated for deduction."
                                    </p>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div className="flex-1 relative">
                         <div className="relative bg-slate-900 rounded-2xl shadow-xl p-8 text-white overflow-hidden">
                            <div className="absolute top-0 right-0 p-32 bg-primary-600 rounded-full blur-[100px] opacity-20"></div>
                            <h3 className="text-lg font-bold mb-6 relative z-10">Limit Tracker</h3>
                            <div className="space-y-6 relative z-10">
                                <div>
                                    <div className="flex justify-between text-sm mb-2">
                                        <span className="text-slate-300">Life Insurance</span>
                                        <span className="text-white font-mono">100% used</span>
                                    </div>
                                    <div className="h-2 bg-slate-700 rounded-full overflow-hidden">
                                        <div className="h-full bg-red-500 w-full"></div>
                                    </div>
                                </div>
                                <div>
                                    <div className="flex justify-between text-sm mb-2">
                                        <span className="text-slate-300">Health Insurance</span>
                                        <span className="text-white font-mono">45% used</span>
                                    </div>
                                    <div className="h-2 bg-slate-700 rounded-full overflow-hidden">
                                        <div className="h-full bg-primary-500 w-[45%]"></div>
                                    </div>
                                </div>
                                <div>
                                    <div className="flex justify-between text-sm mb-2">
                                        <span className="text-slate-300">Donate (2x)</span>
                                        <span className="text-white font-mono">12% used</span>
                                    </div>
                                    <div className="h-2 bg-slate-700 rounded-full overflow-hidden">
                                        <div className="h-full bg-emerald-500 w-[12%]"></div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                {/* All Features Grid */}
                <div className="bg-slate-50 rounded-3xl p-8 lg:p-16">
                    <div className="text-center max-w-2xl mx-auto mb-16">
                        <h2 className="text-3xl font-bold text-slate-900 mb-4">And so much more</h2>
                        <p className="text-slate-500">Explore the complete toolkit designed to make tax filing a breeze.</p>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                        {[
                            { 
                                title: 'Tax Rules Library', 
                                desc: 'Searchable, up-to-date database of all tax deduction rules and limits for 2024-2025.', 
                                icon: BookOpen,
                                color: 'text-accent-600',
                                bg: 'bg-accent-50'
                            },
                            { 
                                title: 'Real-Time Analytics', 
                                desc: 'Visualize your tax savings and remaining deduction allowances in an interactive dashboard.', 
                                icon: PieChart,
                                color: 'text-blue-600',
                                bg: 'bg-blue-50'
                            },
                            { 
                                title: 'Instant Reports', 
                                desc: 'Generate summary reports ready for filing directly with the Revenue Department.', 
                                icon: FileText,
                                color: 'text-slate-600',
                                bg: 'bg-slate-50'
                            },
                        ].map((feature, i) => (
                            <div key={i} className="group p-8 rounded-2xl bg-white border border-slate-100 shadow-sm hover:shadow-md hover:border-primary-100 transition-all">
                                <div className={`h-14 w-14 rounded-xl ${feature.bg} flex items-center justify-center mb-6 ${feature.color} group-hover:scale-110 transition-transform duration-300`}>
                                    <feature.icon size={28} />
                                </div>
                                <h3 className="text-xl font-bold text-slate-900 mb-3">{feature.title}</h3>
                                <p className="text-slate-500 leading-relaxed text-sm">{feature.desc}</p>
                            </div>
                        ))}
                    </div>
                </div>
            </main>
        </div>
    );
};

export default FeaturesPage;
