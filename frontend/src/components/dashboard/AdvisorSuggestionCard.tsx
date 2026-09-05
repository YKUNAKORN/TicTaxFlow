import React from 'react';
import { Lightbulb, CheckCircle2 } from 'lucide-react';
import type { DeductionSuggestion } from '../../types/dashboard';

interface AdvisorSuggestionCardProps {
    suggestion: DeductionSuggestion | null;
    isLoading: boolean;
    hasData: boolean;
    estimatedTaxDue: number;
}

const AdvisorSuggestionCard: React.FC<AdvisorSuggestionCardProps> = ({ suggestion, isLoading, hasData, estimatedTaxDue }) => {
    return (
        <div className="bg-white rounded-xl p-6 shadow-sm border border-slate-200">
            <h3 className="font-semibold text-slate-900 mb-1 flex items-center gap-2">
                <Lightbulb size={18} className="text-amber-500" />
                Advisor Suggestion
            </h3>
            <p className="text-sm text-slate-500 mb-6">Highest-impact way to lower your estimated tax.</p>

            {isLoading ? (
                <div className="space-y-3 animate-pulse" aria-busy="true">
                    <div className="h-4 w-3/4 bg-slate-100 rounded" />
                    <div className="h-3 w-full bg-slate-100 rounded" />
                    <div className="h-3 w-5/6 bg-slate-100 rounded" />
                </div>
            ) : !hasData ? (
                <div className="py-6 text-center text-slate-400">
                    <p className="text-sm">Suggestions appear once income is synced.</p>
                </div>
            ) : !suggestion ? (
                <div className="py-6 text-center">
                    <CheckCircle2 size={28} className="mx-auto mb-2 text-emerald-500" />
                    {estimatedTaxDue <= 0 ? (
                        <>
                            <p className="text-sm font-medium text-slate-700">No tax owed at this income level</p>
                            <p className="text-xs text-slate-400 mt-1">Extra deductions wouldn't save you anything yet.</p>
                        </>
                    ) : (
                        <>
                            <p className="text-sm font-medium text-slate-700">Deduction categories are maxed out</p>
                            <p className="text-xs text-slate-400 mt-1">No further headroom found for this tax year.</p>
                        </>
                    )}
                </div>
            ) : (
                <div>
                    <div className="bg-amber-50 border border-amber-100 rounded-lg p-4">
                        <p className="text-xs font-medium text-amber-700 uppercase tracking-wide">{suggestion.category_name}</p>
                        <p className="text-lg font-bold text-slate-900 mt-1">
                            Top up ฿{suggestion.top_up_amount.toLocaleString()}
                        </p>
                        <p className="text-sm text-slate-600 mt-1">
                            Save ~฿{suggestion.estimated_tax_saving.toLocaleString()} at your {Math.round(suggestion.marginal_rate * 100)}% marginal rate.
                        </p>
                    </div>
                    {suggestion.rule_reference && (
                        <p className="text-xs text-slate-500 mt-3 leading-relaxed line-clamp-4">
                            {suggestion.rule_reference}
                        </p>
                    )}
                </div>
            )}
        </div>
    );
};

export default AdvisorSuggestionCard;
