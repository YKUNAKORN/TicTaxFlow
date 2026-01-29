import React from 'react';
import { TrendingUp, TrendingDown, Minus, DollarSign, FileText, PieChart } from 'lucide-react';
import { clsx } from 'clsx';
import { SummaryStat } from '../../data/mockData';

interface SummaryCardsProps {
    stats: SummaryStat[];
}

const SummaryCards: React.FC<SummaryCardsProps> = ({ stats }) => {
    const getIcon = (label: string) => {
        if (label.includes('Total')) return DollarSign;
        if (label.includes('Usage')) return PieChart;
        if (label.includes('Processed')) return FileText;
        return DollarSign;
    };

    const getTrendIcon = (trend: string) => {
        switch (trend) {
            case 'up': return TrendingUp;
            case 'down': return TrendingDown;
            default: return Minus;
        }
    };

    const getColorClasses = (color: string) => {
        const map: Record<string, string> = {
            blue: 'bg-blue-50 text-blue-600',
            green: 'bg-emerald-50 text-emerald-600',
            slate: 'bg-slate-50 text-slate-600',
        };
        return map[color] || map.slate;
    };

    return (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            {stats.map((stat) => {
                const Icon = getIcon(stat.label);
                const colorClass = getColorClasses(stat.color);
                const TrendIcon = stat.trend ? getTrendIcon(stat.trend) : null;

                return (
                    <div key={stat.label} className="bg-white rounded-xl p-6 shadow-sm border border-slate-100 hover:shadow-md transition-shadow">
                        <div className="flex items-start justify-between">
                            <div>
                                <p className="text-sm font-medium text-slate-500">{stat.label}</p>
                                <h3 className="text-2xl font-bold text-slate-900 mt-2">{stat.value}</h3>
                            </div>
                            <div className={clsx("p-3 rounded-lg", colorClass)}>
                                <Icon size={24} />
                            </div>
                        </div>

                        {stat.subValue && (
                            <div className="mt-4 flex items-center gap-2">
                                {TrendIcon && (
                                    <span className={clsx(
                                        "flex items-center text-xs font-medium",
                                        stat.trend === 'up' ? "text-emerald-600" :
                                            stat.trend === 'down' ? "text-red-600" : "text-slate-500"
                                    )}>
                                        <TrendIcon size={16} className="mr-1" />
                                    </span>
                                )}
                                <span className="text-sm text-slate-500">{stat.subValue}</span>
                            </div>
                        )}
                    </div>
                );
            })}
        </div>
    );
};

export default SummaryCards;
