import React from 'react';
import { AlertTriangle } from 'lucide-react';

interface FinancialOverviewChartProps {
    income: number;
    deductions: number;
    estimatedTax: number;
    bracketsVerified: boolean;
    isLoading: boolean;
    hasData: boolean;
}

interface Row {
    label: string;
    value: string;
    rawValue: number;
    barClass: string;
    badge?: React.ReactNode;
}

const FinancialOverviewChart: React.FC<FinancialOverviewChartProps> = ({
    income,
    deductions,
    estimatedTax,
    bracketsVerified,
    isLoading,
    hasData,
}) => {
    const maxValue = Math.max(income, deductions, estimatedTax, 1);

    const rows: Row[] = [
        {
            label: 'Net Income',
            value: `฿${income.toLocaleString()}`,
            rawValue: income,
            barClass: 'bg-blue-600',
        },
        {
            label: 'Deductions Used',
            value: `฿${deductions.toLocaleString()}`,
            rawValue: deductions,
            barClass: 'bg-emerald-500',
        },
        {
            label: 'Estimated Tax Owed',
            value: `฿${estimatedTax.toLocaleString()}`,
            rawValue: estimatedTax,
            barClass: 'bg-violet-500',
            badge: !bracketsVerified ? (
                <span
                    title="Estimate uses placeholder tax brackets pending Revenue Department verification. Do not treat as a final figure."
                    className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[11px] font-medium bg-amber-100 text-amber-800 cursor-help"
                >
                    <AlertTriangle size={12} /> Unverified brackets
                </span>
            ) : undefined,
        },
    ];

    return (
        <div className="bg-white rounded-xl p-6 shadow-sm border border-slate-200">
            <div className="flex items-center justify-between mb-1">
                <h3 className="font-semibold text-slate-900">Income, Deductions &amp; Estimated Tax</h3>
            </div>
            <p className="text-sm text-slate-500 mb-6">How this year's income compares to what you've deducted and what you may owe.</p>

            {isLoading ? (
                <div className="space-y-5" aria-busy="true">
                    {[0, 1, 2].map((i) => (
                        <div key={i} className="space-y-2 animate-pulse">
                            <div className="h-3 w-28 bg-slate-100 rounded" />
                            <div className="h-3 w-full bg-slate-100 rounded-full" />
                        </div>
                    ))}
                </div>
            ) : !hasData ? (
                <div className="py-8 text-center text-slate-500">
                    <p className="text-sm font-medium text-slate-600">No income data yet</p>
                    <p className="text-xs mt-1">Sync your marketplace income to see this comparison.</p>
                </div>
            ) : (
                <div className="space-y-5">
                    {rows.map((row) => (
                        <div key={row.label}>
                            <div className="flex items-center justify-between text-sm mb-1.5 gap-2">
                                <span className="text-slate-600 flex items-center gap-2">
                                    {row.label}
                                    {row.badge}
                                </span>
                                <span className="font-semibold text-slate-900">{row.value}</span>
                            </div>
                            <div className="h-3 bg-slate-100 rounded-full overflow-hidden">
                                <div
                                    className={`h-full rounded-full ${row.barClass}`}
                                    style={{ width: `${Math.max(2, (row.rawValue / maxValue) * 100)}%` }}
                                />
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

export default FinancialOverviewChart;
