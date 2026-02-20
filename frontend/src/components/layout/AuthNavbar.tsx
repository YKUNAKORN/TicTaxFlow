import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Menu, X } from 'lucide-react';
import logo from '../../assets/logo-icon.png';

const AuthNavbar: React.FC = () => {
    const [isOpen, setIsOpen] = useState(false);
    const location = useLocation();

    // Close menu when clicking a link
    const handleLinkClick = () => setIsOpen(false);

    return (
        <>
            {/* Hamburger Button - Fixed top-left */}
            <button
                onClick={() => setIsOpen(!isOpen)}
                className="fixed top-4 left-4 z-50 p-2.5 rounded-xl bg-white shadow-md text-slate-600 hover:text-slate-900 hover:bg-slate-50 transition-all border border-slate-100"
                aria-label="Toggle menu"
            >
                {isOpen ? <X size={24} /> : <Menu size={24} />}
            </button>

            {/* Backdrop */}
            {isOpen && (
                <div 
                    className="fixed inset-0 bg-slate-900/20 backdrop-blur-sm z-40 transition-opacity"
                    onClick={() => setIsOpen(false)}
                />
            )}

            {/* Slide-out Menu */}
            <div 
                className={`fixed top-0 left-0 h-full w-64 bg-white shadow-2xl z-50 transform transition-transform duration-300 ease-in-out ${
                    isOpen ? 'translate-x-0' : '-translate-x-full'
                }`}
            >
                <div className="flex flex-col h-full">
                    {/* Header */}
                    <div className="p-6 border-b border-slate-100 flex items-center gap-3">
                        <img src={logo} alt="TicTaxFlow" className="h-8 w-8" />
                        <span className="font-bold text-lg text-slate-900">TicTaxFlow</span>
                    </div>

                    {/* Navigation Links */}
                    <nav className="flex-1 px-4 py-6 space-y-2 overflow-y-auto">
                        <Link 
                            to="/" 
                            className={`flex items-center px-4 py-3 rounded-lg text-sm font-medium transition-colors ${
                                location.pathname === '/' 
                                    ? 'bg-primary-50 text-primary-600' 
                                    : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'
                            }`}
                            onClick={handleLinkClick}
                        >
                            Home
                        </Link>
                        <Link 
                            to="/features" 
                            className={`flex items-center px-4 py-3 rounded-lg text-sm font-medium transition-colors ${
                                location.pathname === '/features' 
                                    ? 'bg-primary-50 text-primary-600' 
                                    : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'
                            }`}
                            onClick={handleLinkClick}
                        >
                            Features
                        </Link>
                        <Link 
                            to="/about" 
                            className={`flex items-center px-4 py-3 rounded-lg text-sm font-medium transition-colors ${
                                location.pathname === '/about' 
                                    ? 'bg-primary-50 text-primary-600' 
                                    : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'
                            }`}
                            onClick={handleLinkClick}
                        >
                            About
                        </Link>
                    </nav>

                    {/* Footer Actions */}
                    <div className="p-4 border-t border-slate-100 space-y-3">
                        <Link 
                            to="/signin" 
                            className={`block w-full text-center px-4 py-2.5 rounded-lg text-sm font-medium transition-colors border ${
                                location.pathname === '/signin'
                                    ? 'bg-slate-100 text-slate-900 border-slate-200 cursor-default'
                                    : 'bg-white text-slate-600 border-slate-200 hover:bg-slate-50 hover:text-slate-900'
                            }`}
                            onClick={(e) => {
                                if (location.pathname === '/signin') e.preventDefault();
                                handleLinkClick();
                            }}
                        >
                            Login
                        </Link>
                        <Link 
                            to="/signup" 
                            className={`block w-full text-center px-4 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                                location.pathname === '/signup'
                                    ? 'bg-slate-800 text-white cursor-default'
                                    : 'bg-slate-900 text-white hover:bg-slate-800'
                            }`}
                            onClick={(e) => {
                                if (location.pathname === '/signup') e.preventDefault();
                                handleLinkClick();
                            }}
                        >
                            Get Started
                        </Link>
                    </div>
                </div>
            </div>
        </>
    );
};

export default AuthNavbar;
