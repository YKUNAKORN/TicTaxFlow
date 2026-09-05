import React from 'react';
import type { DeductionsSection } from '../../types/filing';

interface DeductionSummaryProps {
    deductions: DeductionsSection;
}

const DeductionSummary: React.FC<DeductionSummaryProps> = ({ deductions }) => {
    return (
        <div className="bg-white rounded-xl p-6 shadow-sm border border-slate-200">
            <h3 className="font-semibold text-slate-900 mb-1">Deduction summary</h3>
            <p className="text-sm text-slate-500 mb-6">Used vs. remaining in each category</p>

            {deductions.categories.length === 0 ? (
                <p className="text-sm text-slate-500 text-center py-4">No deduction data available</p>
            ) : (
                <div className="space-y-4">
                    {deductions.categories.map((category) => {
                        const percentage = category.max_limit > 0
                            ? Math.min(100, (category.used / category.max_limit) * 100)
                            : (category.used > 0 ? 100 : 0);
                        return (
                            <div key={category.rule_id}>
                                <div className="flex justify-between text-sm mb-1">
                                    <span className="text-slate-600">{category.category_name}</span>
                                    <span className="font-medium text-slate-900">{Math.round(percentage)}%</span>
                                </div>
                                <div className="h-2 bg-slate-100 rounded-full overflow-hidden">
                                    <div
                                        className="h-full bg-primary-500 rounded-full"
                                        style={{ width: `${percentage}%` }}
                                    />
                                </div>
                                <p className="text-xs text-slate-400 mt-1">
                                    ฿{category.used.toLocaleString()} of ฿{category.max_limit.toLocaleString()} limit
                                    {' '}(฿{category.remaining.toLocaleString()} remaining)
                                </p>
                            </div>
                        );
                    })}
                </div>
            )}

            <p className="text-xs text-slate-400 mt-5 pt-4 border-t border-slate-100 leading-relaxed">{deductions.note}</p>
        </div>
    );
};

export default DeductionSummary;
