import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight, CheckCircle, Shield, Zap } from 'lucide-react';

import logo from '../assets/logo-icon.png';

const LandingPage: React.FC = () => {
    return (
        <div className="min-h-screen bg-white">
            {/* Navbar */}
            <nav className="flex items-center justify-between px-6 py-4 max-w-7xl mx-auto">
                <div className="flex items-center gap-2">
                    <img src={logo} alt="Logo" className="h-10 w-auto" />
                    <span className="text-xl font-bold text-slate-900">TicTaxFlow</span>
                </div>
                <div className="hidden md:flex items-center gap-8">
                    <Link to="/tax-rules" className="text-sm font-medium text-slate-600 hover:text-slate-900 transition-colors">Features</Link>
                    <Link to="/dashboard" className="text-sm font-medium text-slate-600 hover:text-slate-900 transition-colors">Pricing</Link>
                    <Link to="/tax-rules" className="text-sm font-medium text-slate-600 hover:text-slate-900 transition-colors">About</Link>
                </div>
                <div className="flex items-center gap-4">
                    <Link to="/signin" className="text-sm font-medium text-slate-600 hover:text-slate-900">Sign In</Link>
                    <Link
                        to="/signup"
                        className="px-4 py-2 bg-slate-900 text-white text-sm font-medium rounded-lg hover:bg-slate-800 transition-colors"
                    >
                        Get Started
                    </Link>
                </div>
            </nav>

            {/* Hero Section */}
            <main className="max-w-7xl mx-auto px-6 py-20 lg:py-32">
                <div className="text-center max-w-3xl mx-auto space-y-8">
                    <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary-50 text-primary-600 text-sm font-medium border border-primary-100 mb-4">
                        <span className="relative flex h-2 w-2">
                            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-primary-400 opacity-75"></span>
                            <span className="relative inline-flex rounded-full h-2 w-2 bg-primary-500"></span>
                        </span>
                        New: AI Receipt Analysis 2.0
                    </div>

                    <h1 className="text-5xl lg:text-7xl font-bold text-slate-900 tracking-tight leading-[1.1]">
                        Tax Deductions, <br />
                        <span className="bg-gradient-to-r from-primary-600 via-secondary-600 to-accent-600 bg-clip-text text-transparent">Simplified by AI.</span>
                    </h1>

                    <p className="text-xl text-slate-500 max-w-2xl mx-auto leading-relaxed">
                        Upload your receipts and let our AI agent analyze, categorize, and optimize your Thai personal income tax deductions in seconds.
                    </p>

                    <div className="flex items-center justify-center gap-4 pt-4">
                        <Link
                            to="/signup"
                            className="flex items-center gap-2 px-8 py-4 bg-primary-600 text-white text-lg font-semibold rounded-xl hover:bg-primary-700 transition-all shadow-lg hover:shadow-primary-600/25 hover:-translate-y-1"
                        >
                            Start Free Trial <ArrowRight size={20} />
                        </Link>
                        <Link to="/transactions" className="px-8 py-4 bg-white text-slate-700 border border-slate-200 text-lg font-semibold rounded-xl hover:bg-slate-50 transition-all">
                            View Demo
                        </Link>
                    </div>
                </div>

                {/* Feature Grid */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mt-24">
                    {[
                        { title: 'Smart Extraction', desc: 'OCR continuously learns from Thai receipts.', icon: Zap },
                        { title: 'Tax Law Compliant', desc: 'Updated with latest Revenue Dept rules.', icon: Shield },
                        { title: 'Instant Reports', desc: 'Download verified summary for filing.', icon: CheckCircle },
                    ].map((feature, i) => (
                        <div key={i} className="p-6 rounded-2xl bg-slate-50 border border-slate-100 hover:border-primary-100 transition-colors">
                            <div className="h-12 w-12 bg-white rounded-xl shadow-sm flex items-center justify-center mb-4 text-primary-600">
                                <feature.icon size={24} />
                            </div>
                            <h3 className="text-lg font-bold text-slate-900 mb-2">{feature.title}</h3>
                            <p className="text-slate-500">{feature.desc}</p>
                        </div>
                    ))}
                </div>
            </main>
        </div>
    );
};

export default LandingPage;
