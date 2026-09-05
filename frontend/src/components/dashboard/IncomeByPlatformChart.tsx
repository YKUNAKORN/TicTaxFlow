import React from 'react';
import { ShoppingBag } from 'lucide-react';
import type { IncomePlatformTotals } from '../../types/dashboard';

interface IncomeByPlatformChartProps {
    platformTotals: IncomePlatformTotals;
    isLoading: boolean;
    hasData: boolean;
}

const PLATFORM_COLORS: Record<string, string> = {
    Shopee: 'bg-orange-500',
    Lazada: 'bg-blue-600',
    TikTokShop: 'bg-slate-800',
};

const IncomeByPlatformChart: React.FC<IncomeByPlatformChartProps> = ({ platformTotals, isLoading, hasData }) => {
    const rows = Object.entries(platformTotals)
        .map(([platform, totals]) => ({ platform, ...totals }))
        .sort((a, b) => b.net_amount - a.net_amount);

    const maxValue = Math.max(...rows.map((r) => r.net_amount), 1);

    return (
        <div className="bg-white rounded-xl p-6 shadow-sm border border-slate-200">
            <div className="flex items-center justify-between mb-1">
                <h3 className="font-semibold text-slate-900">Income by Platform</h3>
            </div>
            <p className="text-sm text-slate-500 mb-6">Net income after marketplace fees, this period.</p>

            {isLoading ? (
                <div className="space-y-4" aria-busy="true">
                    {[0, 1, 2].map((i) => (
                        <div key={i} className="space-y-2 animate-pulse">
                            <div className="h-3 w-20 bg-slate-100 rounded" />
                            <div className="h-3 w-full bg-slate-100 rounded-full" />
                        </div>
                    ))}
                </div>
            ) : !hasData || rows.length === 0 ? (
                <div className="py-8 text-center text-slate-400">
                    <ShoppingBag size={32} className="mx-auto mb-2 opacity-40" />
                    <p className="text-sm font-medium text-slate-600">No marketplace sales synced</p>
                    <p className="text-xs mt-1">Shopee, Lazada, and TikTok Shop sales will appear here.</p>
                </div>
            ) : (
                <div className="space-y-4">
                    {rows.map((row) => (
                        <div key={row.platform}>
                            <div className="flex items-center justify-between text-sm mb-1.5">
                                <span className="text-slate-700 font-medium">{row.platform}</span>
                                <span className="text-slate-500">
                                    ฿{row.net_amount.toLocaleString()}
                                    <span className="text-slate-400"> · {row.record_count} orders</span>
                                </span>
                            </div>
                            <div className="h-2.5 bg-slate-100 rounded-full overflow-hidden">
                                <div
                                    className={`h-full rounded-full ${PLATFORM_COLORS[row.platform] || 'bg-slate-400'}`}
                                    style={{ width: `${Math.max(2, (row.net_amount / maxValue) * 100)}%` }}
                                />
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

export default IncomeByPlatformChart;
