import React, { useState } from 'react';

interface DocumentChecklistProps {
    items: string[];
}

const DocumentChecklist: React.FC<DocumentChecklistProps> = ({ items }) => {
    const [checked, setChecked] = useState<Record<number, boolean>>({});

    const toggle = (index: number) => {
        setChecked((prev) => ({ ...prev, [index]: !prev[index] }));
    };

    return (
        <div className="bg-white rounded-xl p-6 shadow-sm border border-slate-200">
            <h3 className="font-semibold text-slate-900 mb-1">Documents to prepare</h3>
            <p className="text-sm text-slate-500 mb-4">Check items off for yourself — not saved to the system</p>

            <ul className="space-y-2.5">
                {items.map((item, index) => (
                    <li key={index}>
                        <label className="flex items-start gap-3 text-sm text-slate-700 cursor-pointer">
                            <input
                                type="checkbox"
                                checked={!!checked[index]}
                                onChange={() => toggle(index)}
                                className="mt-0.5 h-4 w-4 rounded border-slate-300 text-primary-600 focus:ring-primary-500"
                            />
                            <span className={checked[index] ? 'line-through text-slate-400' : ''}>{item}</span>
                        </label>
                    </li>
                ))}
            </ul>
        </div>
    );
};

export default DocumentChecklist;
