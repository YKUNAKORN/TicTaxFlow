import React, { useState, useEffect } from 'react';
import { 
    BookOpen, Search, Filter, Calendar, TrendingUp, AlertCircle, Info 
} from 'lucide-react';
import { taxRulesApi } from '../api';

interface TaxRule {
    id: number;
    category_name: string;
    max_limit: number;
    tax_year: number;
    is_active: boolean;
}

const TaxRulesPage: React.FC = () => {
    const [rules, setRules] = useState<TaxRule[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState('');
    const [searchTerm, setSearchTerm] = useState('');
    const [selectedYear, setSelectedYear] = useState<number>(2025);

    useEffect(() => {
        fetchTaxRules();
    }, [selectedYear]);

    const fetchTaxRules = async () => {
        setIsLoading(true);
        setError('');
        try {
            // Fetch for the selected year
            const response = await taxRulesApi.getAllTaxRules(selectedYear);
            console.log('Tax rules response:', response);
            if (response.success) {
                setRules(response.data || []);
            } else if (Array.isArray(response)) {
                // Fallback if API returns array directly
                setRules(response);
            }
        } catch (err: any) {
            console.error('Failed to fetch tax rules:', err);
            setError(err.message || 'Failed to load tax rules');
        } finally {
            setIsLoading(false);
        }
    };

    const filteredRules = rules.filter(rule => 
        rule.category_name.toLowerCase().includes(searchTerm.toLowerCase())
    );

    // Group rules by limit range for quick stats (optional enhancement)
    const highValueDeductions = rules.filter(r => r.max_limit >= 100000).length;
    
    if (isLoading) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
                    <p className="text-slate-600">Loading tax rules...</p>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="flex flex-col items-center justify-center p-8 bg-red-50 rounded-xl border border-red-100 text-center">
                <AlertCircle size={48} className="text-red-400 mb-4" />
                <h3 className="text-lg font-semibold text-red-800">Unable to Load Rules</h3>
                <p className="text-red-600 mt-2 max-w-md">{error}</p>
                <button 
                    onClick={fetchTaxRules}
                    className="mt-6 px-4 py-2 bg-white border border-red-200 text-red-700 rounded-lg hover:bg-red-50 font-medium shadow-sm transition-colors"
                >
                    Retry
                </button>
            </div>
        );
    }

    return (
        <div className="space-y-8 animate-fade-in">
            {/* Header Section */}
            <div className="bg-gradient-to-r from-primary-600 to-primary-700 rounded-2xl p-8 text-white shadow-lg relative overflow-hidden">
                <div className="absolute top-0 right-0 p-4 opacity-10">
                    <BookOpen size={120} className="transform rotate-12 translate-x-8 -translate-y-8" />
                </div>
                <div className="relative z-10">
                    <h1 className="text-3xl font-bold mb-2">Tax Rules Library</h1>
                    <p className="text-primary-100 max-w-xl text-lg">
                        Comprehensive guide to Thai Revenue Department tax deduction allowances for the year {selectedYear}.
                    </p>
                    
                    <div className="flex flex-col sm:flex-row gap-4 mt-8">
                        {/* Search Input */}
                        <div className="relative flex-1">
                            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                <Search className="h-5 w-5 text-primary-700" />
                            </div>
                            <input
                                type="text"
                                className="block w-full pl-10 pr-4 py-3 bg-white/90 backdrop-blur border-0 rounded-xl text-slate-900 placeholder-slate-500 focus:ring-2 focus:ring-white/50 transition-all shadow-sm"
                                placeholder="Search tax categories (e.g., Insurance, ESG)..."
                                value={searchTerm}
                                onChange={(e) => setSearchTerm(e.target.value)}
                            />
                        </div>

                        {/* Year Selector */}
                        <div className="relative min-w-[140px]">
                            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                <Calendar className="h-5 w-5 text-primary-700" />
                            </div>
                            <select
                                value={selectedYear}
                                onChange={(e) => setSelectedYear(Number(e.target.value))}
                                className="block w-full pl-10 pr-8 py-3 bg-white/90 backdrop-blur border-0 rounded-xl text-slate-900 font-medium focus:ring-2 focus:ring-white/50 cursor-pointer shadow-sm appearance-none"
                            >
                                <option value={2025}>Tax Year 2025</option>
                                <option value={2024}>Tax Year 2024</option>
                            </select>
                            <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
                                <svg className="h-4 w-4 text-slate-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                                </svg>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Stats Overview */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex items-center gap-4">
                    <div className="p-3 bg-primary-50 text-primary-600 rounded-lg">
                        <BookOpen size={24} />
                    </div>
                    <div>
                        <p className="text-sm text-slate-500 font-medium">Total Categories</p>
                        <p className="text-2xl font-bold text-slate-900">{rules.length}</p>
                    </div>
                </div>
                
                <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex items-center gap-4">
                    <div className="p-3 bg-secondary-50 text-secondary-600 rounded-lg">
                        <TrendingUp size={24} />
                    </div>
                    <div>
                        <p className="text-sm text-slate-500 font-medium">High Value Deductions</p>
                        <p className="text-2xl font-bold text-slate-900">{highValueDeductions}</p>
                    </div>
                </div>

                <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex items-center gap-4">
                    <div className="p-3 bg-accent-50 text-accent-600 rounded-lg">
                        <Info size={24} />
                    </div>
                    <div>
                        <p className="text-sm text-slate-500 font-medium">Updated Status</p>
                        <p className="text-2xl font-bold text-slate-900">Current</p>
                    </div>
                </div>
            </div>

            {/* Rules Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {filteredRules.length > 0 ? (
                    filteredRules.map((rule) => {
                        // Determine visual style based on limit amount
                        const isHighValue = rule.max_limit >= 100000;
                        const cardBorderColor = isHighValue ? 'border-primary-200' : 'border-slate-200';
                        const iconBgColor = isHighValue ? 'bg-primary-50' : 'bg-slate-50';
                        const iconColor = isHighValue ? 'text-primary-600' : 'text-slate-500';

                        return (
                            <div 
                                key={rule.id} 
                                className={`bg-white rounded-xl border ${cardBorderColor} p-6 shadow-sm hover:shadow-md transition-shadow group relative overflow-hidden`}
                            >
                                <div className="flex justify-between items-start mb-4">
                                    <div className={`h-12 w-12 rounded-lg ${iconBgColor} flex items-center justify-center ${iconColor} group-hover:scale-110 transition-transform`}>
                                        <BookOpen size={24} />
                                    </div>
                                    <span className={`px-2 py-1 rounded text-xs font-semibold ${rule.is_active ? 'bg-green-100 text-green-700' : 'bg-slate-100 text-slate-500'}`}>
                                        {rule.is_active ? 'Active' : 'Inactive'}
                                    </span>
                                </div>
                                
                                <h3 className="text-lg font-bold text-slate-900 mb-2 group-hover:text-primary-700 transition-colors">
                                    {rule.category_name}
                                </h3>
                                
                                <div className="mt-4 pt-4 border-t border-slate-100">
                                    <div className="flex justify-between items-end">
                                        <div>
                                            <p className="text-xs text-slate-500 uppercase tracking-wide font-semibold mb-1">Max Deduction</p>
                                            <p className="text-xl font-bold text-slate-900">
                                                {rule.max_limit > 0 ? `฿${rule.max_limit.toLocaleString()}` : 'Unlimited'}
                                            </p>
                                        </div>
                                        <span className="text-xs font-mono text-slate-400">
                                            Year {rule.tax_year}
                                        </span>
                                    </div>
                                </div>
                            </div>
                        );
                    })
                ) : (
                    <div className="col-span-full py-12 text-center bg-slate-50 rounded-xl border-2 border-dashed border-slate-200">
                        <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-slate-100 mb-4">
                            <Search size={24} className="text-slate-400" />
                        </div>
                        <h3 className="text-lg font-medium text-slate-900">No matching rules found</h3>
                        <p className="text-slate-500 mt-1">Try adjusting your search terms or year filter.</p>
                        <button 
                            onClick={() => { setSearchTerm(''); setSelectedYear(2025); }}
                            className="mt-4 text-primary-600 hover:text-primary-700 font-medium"
                        >
                            Clear filters
                        </button>
                    </div>
                )}
            </div>
        </div>
    );
};

export default TaxRulesPage;
