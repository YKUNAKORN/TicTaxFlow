import React, { useState, useEffect } from 'react';
import { User, Mail, DollarSign, Save, AlertCircle, CheckCircle, Loader, Lock, Key } from 'lucide-react';
import { profileApi, authApi } from '../api';
import { ApiError } from '../api/client';
import type { UserProfile, ProfileUpdate } from '../types/profile';

const ProfilePage: React.FC = () => {
    const [profile, setProfile] = useState<UserProfile | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [isSaving, setIsSaving] = useState(false);
    const [isChangingPassword, setIsChangingPassword] = useState(false);
    const [error, setError] = useState('');
    const [successMessage, setSuccessMessage] = useState('');
    const [passwordError, setPasswordError] = useState('');
    const [passwordSuccess, setPasswordSuccess] = useState('');

    const [formData, setFormData] = useState({
        full_name: '',
        annual_income: '',
    });

    const [passwordData, setPasswordData] = useState({
        current_password: '',
        new_password: '',
        confirm_password: '',
    });

    useEffect(() => {
        loadProfile();
    }, []);

    const loadProfile = async () => {
        setIsLoading(true);
        setError('');
        
        try {
            const response = await profileApi.getMe();
            setProfile(response.data);
            setFormData({
                full_name: response.data.full_name || '',
                annual_income: response.data.annual_income?.toString() || '',
            });
        } catch (err) {
            if (err instanceof ApiError) {
                setError(err.message);
            } else {
                setError('Failed to load profile');
            }
        } finally {
            setIsLoading(false);
        }
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        setSuccessMessage('');
        setIsSaving(true);

        try {
            const updates: ProfileUpdate = {
                full_name: formData.full_name || undefined,
                annual_income: formData.annual_income ? parseFloat(formData.annual_income) : undefined,
            };

            await profileApi.updateMe(updates);
            setSuccessMessage('Profile updated successfully');
            
            setTimeout(() => {
                setSuccessMessage('');
            }, 3000);

            await loadProfile();
        } catch (err) {
            if (err instanceof ApiError) {
                setError(err.message);
            } else {
                setError('Failed to update profile');
            }
        } finally {
            setIsSaving(false);
        }
    };

    const handleInputChange = (field: string, value: string) => {
        setFormData(prev => ({
            ...prev,
            [field]: value
        }));
    };

    const handlePasswordChange = async (e: React.FormEvent) => {
        e.preventDefault();
        setPasswordError('');
        setPasswordSuccess('');

        if (passwordData.new_password !== passwordData.confirm_password) {
            setPasswordError('New passwords do not match');
            return;
        }

        if (passwordData.new_password.length < 6) {
            setPasswordError('New password must be at least 6 characters');
            return;
        }

        setIsChangingPassword(true);

        try {
            await authApi.changePassword({
                current_password: passwordData.current_password,
                new_password: passwordData.new_password,
            });

            setPasswordSuccess('Password changed successfully');
            setPasswordData({
                current_password: '',
                new_password: '',
                confirm_password: '',
            });

            setTimeout(() => {
                setPasswordSuccess('');
            }, 3000);
        } catch (err) {
            if (err instanceof ApiError) {
                setPasswordError(err.message);
            } else {
                setPasswordError('Failed to change password');
            }
        } finally {
            setIsChangingPassword(false);
        }
    };

    if (isLoading) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
                    <p className="text-slate-600">Loading profile...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            <div className="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden">
                <div className="bg-gradient-to-r from-primary-500 to-primary-600 px-6 py-8">
                    <div className="flex items-center gap-4">
                        <div className="h-20 w-20 rounded-full bg-white flex items-center justify-center shadow-lg">
                            <User size={40} className="text-primary-600" />
                        </div>
                        <div className="text-white">
                            <h1 className="text-2xl font-bold">{profile?.full_name || 'User Profile'}</h1>
                            <p className="text-primary-100 mt-1">{profile?.email}</p>
                        </div>
                    </div>
                </div>

                <div className="p-6">
                    {error && (
                        <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg flex items-center gap-3 text-red-800">
                            <AlertCircle className="h-5 w-5 flex-shrink-0" />
                            <span className="text-sm">{error}</span>
                        </div>
                    )}

                    {successMessage && (
                        <div className="mb-4 p-4 bg-green-50 border border-green-200 rounded-lg flex items-center gap-3 text-green-800">
                            <CheckCircle className="h-5 w-5 flex-shrink-0" />
                            <span className="text-sm">{successMessage}</span>
                        </div>
                    )}

                    <form onSubmit={handleSubmit} className="space-y-6">
                        <div>
                            <label className="block text-sm font-medium text-slate-700 mb-2">
                                Full Name
                            </label>
                            <div className="relative">
                                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                    <User className="h-5 w-5 text-slate-400" />
                                </div>
                                <input
                                    type="text"
                                    value={formData.full_name}
                                    onChange={(e) => handleInputChange('full_name', e.target.value)}
                                    disabled={isSaving}
                                    className="block w-full pl-10 pr-3 py-3 border border-slate-200 rounded-xl text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all bg-slate-50 hover:bg-white disabled:opacity-50 disabled:cursor-not-allowed"
                                    placeholder="Enter your full name"
                                />
                            </div>
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-slate-700 mb-2">
                                Email Address
                            </label>
                            <div className="relative">
                                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                    <Mail className="h-5 w-5 text-slate-400" />
                                </div>
                                <input
                                    type="email"
                                    value={profile?.email || ''}
                                    disabled
                                    className="block w-full pl-10 pr-3 py-3 border border-slate-200 rounded-xl text-slate-500 bg-slate-100 cursor-not-allowed"
                                    placeholder="Email cannot be changed"
                                />
                            </div>
                            <p className="mt-1 text-xs text-slate-500">Email address cannot be changed</p>
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-slate-700 mb-2">
                                Annual Income (THB)
                            </label>
                            <div className="relative">
                                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                    <DollarSign className="h-5 w-5 text-slate-400" />
                                </div>
                                <input
                                    type="number"
                                    value={formData.annual_income}
                                    onChange={(e) => handleInputChange('annual_income', e.target.value)}
                                    disabled={isSaving}
                                    className="block w-full pl-10 pr-3 py-3 border border-slate-200 rounded-xl text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all bg-slate-50 hover:bg-white disabled:opacity-50 disabled:cursor-not-allowed"
                                    placeholder="500000"
                                    min="0"
                                    step="1000"
                                />
                            </div>
                            <p className="mt-1 text-xs text-slate-500">Used for tax calculations and deduction limits</p>
                        </div>

                        <button
                            type="submit"
                            disabled={isSaving}
                            className="w-full flex items-center justify-center gap-2 py-3 px-4 bg-primary-600 text-white font-semibold rounded-xl hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 transition-all shadow-lg hover:shadow-primary-500/25 disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            {isSaving ? (
                                <>
                                    <Loader className="animate-spin" size={18} />
                                    Saving...
                                </>
                            ) : (
                                <>
                                    <Save size={18} />
                                    Save Changes
                                </>
                            )}
                        </button>
                    </form>
                </div>
            </div>

            <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-6">
                <h2 className="text-lg font-semibold text-slate-900 mb-4">Account Information</h2>
                <div className="space-y-3 text-sm">
                    <div className="flex justify-between py-2 border-b border-slate-100">
                        <span className="text-slate-500">User ID</span>
                        <span className="text-slate-900 font-mono text-xs">{profile?.id}</span>
                    </div>
                    <div className="flex justify-between py-2 border-b border-slate-100">
                        <span className="text-slate-500">Account Created</span>
                        <span className="text-slate-900">
                            {profile?.created_at ? new Date(profile.created_at).toLocaleDateString() : 'N/A'}
                        </span>
                    </div>
                </div>
            </div>

            <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-6">
                <div className="flex items-center gap-3 mb-6">
                    <div className="h-10 w-10 rounded-full bg-primary-50 flex items-center justify-center">
                        <Key className="text-primary-600" size={20} />
                    </div>
                    <div>
                        <h2 className="text-lg font-semibold text-slate-900">Change Password</h2>
                        <p className="text-sm text-slate-500">Update your account password</p>
                    </div>
                </div>

                {passwordError && (
                    <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg flex items-center gap-3 text-red-800">
                        <AlertCircle className="h-5 w-5 flex-shrink-0" />
                        <span className="text-sm">{passwordError}</span>
                    </div>
                )}

                {passwordSuccess && (
                    <div className="mb-4 p-4 bg-green-50 border border-green-200 rounded-lg flex items-center gap-3 text-green-800">
                        <CheckCircle className="h-5 w-5 flex-shrink-0" />
                        <span className="text-sm">{passwordSuccess}</span>
                    </div>
                )}

                <form onSubmit={handlePasswordChange} className="space-y-4">
                    <div>
                        <label className="block text-sm font-medium text-slate-700 mb-2">
                            Current Password
                        </label>
                        <div className="relative">
                            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                <Lock className="h-5 w-5 text-slate-400" />
                            </div>
                            <input
                                type="password"
                                value={passwordData.current_password}
                                onChange={(e) => setPasswordData(prev => ({ ...prev, current_password: e.target.value }))}
                                disabled={isChangingPassword}
                                required
                                className="block w-full pl-10 pr-3 py-3 border border-slate-200 rounded-xl text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all bg-slate-50 hover:bg-white disabled:opacity-50 disabled:cursor-not-allowed"
                                placeholder="Enter current password"
                            />
                        </div>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-slate-700 mb-2">
                            New Password
                        </label>
                        <div className="relative">
                            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                <Lock className="h-5 w-5 text-slate-400" />
                            </div>
                            <input
                                type="password"
                                value={passwordData.new_password}
                                onChange={(e) => setPasswordData(prev => ({ ...prev, new_password: e.target.value }))}
                                disabled={isChangingPassword}
                                required
                                className="block w-full pl-10 pr-3 py-3 border border-slate-200 rounded-xl text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all bg-slate-50 hover:bg-white disabled:opacity-50 disabled:cursor-not-allowed"
                                placeholder="Enter new password"
                            />
                        </div>
                        <p className="mt-1 text-xs text-slate-500">Minimum 6 characters</p>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-slate-700 mb-2">
                            Confirm New Password
                        </label>
                        <div className="relative">
                            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                <Lock className="h-5 w-5 text-slate-400" />
                            </div>
                            <input
                                type="password"
                                value={passwordData.confirm_password}
                                onChange={(e) => setPasswordData(prev => ({ ...prev, confirm_password: e.target.value }))}
                                disabled={isChangingPassword}
                                required
                                className="block w-full pl-10 pr-3 py-3 border border-slate-200 rounded-xl text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all bg-slate-50 hover:bg-white disabled:opacity-50 disabled:cursor-not-allowed"
                                placeholder="Confirm new password"
                            />
                        </div>
                    </div>

                    <button
                        type="submit"
                        disabled={isChangingPassword}
                        className="w-full flex items-center justify-center gap-2 py-3 px-4 bg-primary-600 text-white font-semibold rounded-xl hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 transition-all shadow-lg hover:shadow-primary-500/25 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        {isChangingPassword ? (
                            <>
                                <Loader className="animate-spin" size={18} />
                                Changing Password...
                            </>
                        ) : (
                            <>
                                <Key size={18} />
                                Change Password
                            </>
                        )}
                    </button>
                </form>
            </div>
        </div>
    );
};

export default ProfilePage;
