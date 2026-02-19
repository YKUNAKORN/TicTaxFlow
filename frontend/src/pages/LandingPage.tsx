import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight, CheckCircle, Shield, Zap } from 'lucide-react';

import logo from '../assets/logo-icon.png';

const LandingPage: React.FC = () => {
    return (
        <div className="min-h-screen bg-white">
            {/* Navbar */}
            <nav className="fixed top-0 w-full z-50 bg-white/80 backdrop-blur-sm border-b border-slate-100">
                <div className="flex items-center justify-between px-6 py-4 max-w-7xl mx-auto">
                    <div className="flex items-center gap-2">
                        <img src={logo} alt="Logo" className="h-10 w-auto" />
                        <span className="text-xl font-bold text-slate-900">TicTaxFlow</span>
                    </div>
                    <div className="hidden md:flex items-center gap-8">
                        <Link to="/" className="text-sm font-medium text-slate-600 hover:text-slate-900 transition-colors">Home</Link>
                        <Link to="/features" className="text-sm font-medium text-slate-600 hover:text-slate-900 transition-colors">Features</Link>
                        <Link to="/about" className="text-sm font-medium text-slate-600 hover:text-slate-900 transition-colors">About</Link>
                    </div>
                    <div className="flex items-center gap-4">
                        <Link to="/signin" className="text-sm font-medium text-slate-600 hover:text-slate-900">Login</Link>
                        <Link
                            to="/signup"
                            className="px-4 py-2 bg-slate-900 text-white text-sm font-medium rounded-lg hover:bg-slate-800 transition-colors"
                        >
                            Get Started
                        </Link>
                    </div>
                </div>
            </nav>

            {/* Hero Section */}
            <main className="h-screen flex items-center justify-center px-6 relative">
                <div className="text-center max-w-3xl mx-auto space-y-8 animate-fade-in-up">
                    <h1 className="text-5xl lg:text-7xl font-bold text-slate-900 tracking-tight leading-[1.1]">
                        Tax Deductions, <br />
                        <span className="bg-[linear-gradient(to_right,#7B3FFF,#FF46A4,#FDC830,#7B3FFF)] bg-[length:200%_auto] animate-shine bg-clip-text text-transparent">Simplified by AI.</span>
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
                        <Link to="/features" className="px-8 py-4 bg-white text-slate-700 border border-slate-200 text-lg font-semibold rounded-xl hover:bg-slate-50 transition-all">
                            View Features
                        </Link>
                    </div>
                </div>
            </main>
        </div>
    );
};

export default LandingPage;
