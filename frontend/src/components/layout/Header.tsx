import React, { useEffect, useState } from 'react';
import { Menu, User, Bell } from 'lucide-react';
import { profileApi } from '../../api/profile';
import type { UserProfile } from '../../types/profile';

interface HeaderProps {
    onMenuClick: () => void;
    title?: string;
}

const Header: React.FC<HeaderProps> = ({ onMenuClick, title = "Dashboard" }) => {
    const [userProfile, setUserProfile] = useState<UserProfile | null>(null);

    useEffect(() => {
        fetchUserProfile();
    }, []);

    const fetchUserProfile = async () => {
        try {
            const response = await profileApi.getMe();
            if (response.success) {
                setUserProfile(response.data);
            }
        } catch (error) {
            console.error('Failed to fetch user profile:', error);
        }
    };

    const displayName = userProfile?.username || userProfile?.full_name || 'User';

    return (
        <header className="sticky top-0 z-10 flex h-16 items-center justify-between border-b border-slate-200 bg-white/80 px-6 backdrop-blur-sm lg:px-8">
            <div className="flex items-center gap-4">
                <button
                    onClick={onMenuClick}
                    className="text-slate-500 hover:text-slate-700 lg:hidden"
                >
                    <Menu size={24} />
                </button>
                <h1 className="text-xl font-semibold text-slate-900">{title}</h1>
            </div>

            <div className="flex items-center gap-4">
                <button className="relative text-slate-400 hover:text-slate-600">
                    <Bell size={20} />
                    <span className="absolute top-0 right-0 h-2 w-2 rounded-full bg-red-500 ring-2 ring-white"></span>
                </button>

                <div className="h-8 w-px bg-slate-200 mx-1"></div>

                <div className="flex items-center gap-3">
                    <div className="hidden text-right md:block">
                        <p className="text-sm font-medium text-slate-900">{displayName}</p>
                        <p className="text-xs text-slate-500">Tax Payer</p>
                    </div>
                    <div className="h-10 w-10 rounded-full bg-slate-100 flex items-center justify-center border border-slate-200">
                        <User size={20} className="text-slate-600" />
                    </div>
                </div>
            </div>
        </header>
    );
};

export default Header;
