import React, { useState } from 'react';
import { Copy, Check } from 'lucide-react';
import type { BoxMappingRow } from '../../types/filing';

interface BoxMappingTableProps {
    rows: BoxMappingRow[];
}

const CopyValueButton: React.FC<{ value: number; copied: boolean; onCopy: () => void }> = ({ value, copied, onCopy }) => (
    <span className="inline-flex items-center gap-1.5">
        <button
            type="button"
            onClick={onCopy}
            className="print:hidden inline-flex items-center gap-1.5 rounded-md border border-slate-200 px-2 py-1 text-xs font-medium text-slate-600 hover:bg-slate-50 hover:border-primary-200 transition-colors"
            title="Copy the raw number (no baht sign or thousands separator)"
        >
            {copied ? (
                <>
                    <Check size={13} className="text-emerald-600" /> Copied
                </>
            ) : (
                <>
                    <Copy size={13} /> Copy
                </>
            )}
        </button>
        {/* Rendered as plain text (not inside the button) so the value
            survives the print stylesheet's `button { display: none }` --
            the printed pack must still show every figure. */}
        <span className="font-semibold text-slate-900">฿{value.toLocaleString()}</span>
    </span>
);

const BoxMappingTable: React.FC<BoxMappingTableProps> = ({ rows }) => {
    const [copiedIndex, setCopiedIndex] = useState<number | null>(null);

    const handleCopy = async (index: number, value: number) => {
        try {
            await navigator.clipboard.writeText(String(value));
            setCopiedIndex(index);
            setTimeout(() => setCopiedIndex((current) => (current === index ? null : current)), 1800);
        } catch (err) {
            console.error('Failed to copy value:', err);
        }
    };

    return (
        <div className="bg-white rounded-xl p-6 shadow-sm border border-slate-200">
            <h3 className="font-semibold text-slate-900 mb-1">Form box mapping</h3>
            <p className="text-sm text-slate-500 mb-6">Copy each value into the Revenue Department's e-Filing system</p>

            {/* Desktop / tablet: table */}
            <div className="hidden sm:block overflow-x-auto">
                <table className="w-full text-sm">
                    <thead>
                        <tr className="text-left text-xs text-slate-400 uppercase tracking-wide border-b border-slate-100">
                            <th className="pb-3 font-medium">Item</th>
                            <th className="pb-3 font-medium">Form reference</th>
                            <th className="pb-3 font-medium text-right">Value</th>
                        </tr>
                    </thead>
                    <tbody>
                        {rows.map((row, index) => (
                            <tr key={row.form_item} className="border-b border-slate-50 align-top break-inside-avoid">
                                <td className="py-3 pr-4">
                                    <p className="font-medium text-slate-900">{row.label_en}</p>
                                    <p className="text-xs text-slate-400 mt-0.5">{row.label_th}</p>
                                    {row.note && <p className="text-[11px] text-slate-400 mt-1.5 leading-relaxed max-w-md">{row.note}</p>}
                                </td>
                                <td className="py-3 pr-4 text-slate-600">{row.form_item}</td>
                                <td className="py-3 text-right">
                                    <CopyValueButton
                                        value={row.value}
                                        copied={copiedIndex === index}
                                        onCopy={() => handleCopy(index, row.value)}
                                    />
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>

            {/* Mobile: stacked cards */}
            <div className="sm:hidden space-y-3">
                {rows.map((row, index) => (
                    <div key={row.form_item} className="rounded-lg border border-slate-100 p-4 break-inside-avoid">
                        <p className="font-medium text-slate-900 text-sm">{row.label_en}</p>
                        <p className="text-xs text-slate-400 mt-0.5">{row.label_th}</p>
                        <p className="text-xs text-slate-500 mt-2">{row.form_item}</p>
                        {row.note && <p className="text-[11px] text-slate-400 mt-1.5 leading-relaxed">{row.note}</p>}
                        <div className="mt-3">
                            <CopyValueButton
                                value={row.value}
                                copied={copiedIndex === index}
                                onCopy={() => handleCopy(index, row.value)}
                            />
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default BoxMappingTable;
