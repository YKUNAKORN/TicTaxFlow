import React, { ReactNode } from 'react';
import { LayoutDashboard, Receipt, BookOpen, LogOut, X, Bot } from 'lucide-react';
import { clsx } from 'clsx';
import { NavLink } from 'react-router-dom';

interface SidebarProps {
    isOpen: boolean;
    onClose: () => void;
}

import logo from '../../assets/logo-icon.png';

const Sidebar: React.FC<SidebarProps> = ({ isOpen, onClose }) => {
    const navItems = [
        { icon: LayoutDashboard, label: 'Dashboard', path: '/dashboard' },
        { icon: Receipt, label: 'Transactions', path: '/transactions' },
        { icon: Bot, label: 'AI Agent', path: '/agent' },
        { icon: BookOpen, label: 'Tax Rules (AI Docs)', path: '/tax-rules' },
    ];

    return (
        <>
            {/* Mobile Overlay */}
            {isOpen && (
                <div
                    className="fixed inset-0 bg-slate-900/20 backdrop-blur-sm z-20 lg:hidden"
                    onClick={onClose}
                />
            )}

            {/* Sidebar Container */}
            <aside
                className={clsx(
                    "fixed top-0 left-0 z-30 h-screen w-64 bg-white border-r border-slate-200 transition-transform duration-300 ease-in-out lg:translate-x-0 shadow-sm",
                    isOpen ? "translate-x-0" : "-translate-x-full"
                )}
            >
                <div className="flex h-16 items-center justify-between px-6 border-b border-slate-100">
                    <div className="flex items-center gap-2">
                        <img src={logo} alt="Logo" className="h-10 w-auto" />
                        <span className="text-xl font-bold text-primary-600 tracking-tight">TicTaxFlow</span>
                    </div>
                    <button onClick={onClose} className="lg:hidden text-slate-400 hover:text-slate-600">
                        <X size={24} />
                    </button>
                </div>

                <nav className="flex-1 px-4 py-6 space-y-2">
                    {navItems.map((item) => (
                        <NavLink
                            key={item.path}
                            to={item.path}
                            onClick={() => { if (window.innerWidth < 1024) onClose(); }}
                            className={({ isActive }) => clsx(
                                "flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-all duration-200",
                                isActive
                                    ? "bg-primary-50 text-primary-700 shadow-sm ring-1 ring-primary-100"
                                    : "text-slate-500 hover:text-slate-700 hover:bg-slate-50"
                            )}
                        >
                            {({ isActive }) => (
                                <>
                                    <item.icon size={20} className={isActive ? "text-primary-600" : "text-slate-400"} />
                                    {item.label}
                                </>
                            )}
                        </NavLink>
                    ))}
                </nav>

                <div className="p-4 border-t border-slate-100">
                    <NavLink to="/" className="flex items-center gap-3 w-full px-4 py-3 text-sm text-slate-500 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors group">
                        <LogOut size={20} className="group-hover:text-red-500" />
                        Sign Out
                    </NavLink>
                </div>
            </aside>
        </>
    );
};

export default Sidebar;
