import React from 'react';
import { Calendar, Clock } from 'lucide-react';
import { clsx } from 'clsx';
import type { FilingDeadline, FilingFormSummary, FormType } from '../../types/filing';

interface FormPickerProps {
    forms: FilingFormSummary[];
    selected: FormType;
    onSelect: (formType: FormType) => void;
}

const FORM_META: Record<FormType, { name: string; covers: string }> = {
    PND94: { name: 'ภ.ง.ด.94', covers: 'รายได้ ม.ค.–มิ.ย. (ยื่นกลางปี)' },
    PND90: { name: 'ภ.ง.ด.90', covers: 'รายได้ทั้งปี (ยื่นประจำปี)' },
};

type Tone = 'calm' | 'soon' | 'urgent' | 'overdue';

function toneFor(deadline: FilingDeadline): Tone {
    if (deadline.is_overdue) return 'overdue';
    if (deadline.days_remaining <= 7) return 'urgent';
    if (deadline.days_remaining <= 30) return 'soon';
    return 'calm';
}

const TONE_BADGE: Record<Tone, string> = {
    calm: 'bg-slate-100 text-slate-600',
    soon: 'bg-accent-100 text-accent-600',
    urgent: 'bg-secondary-100 text-secondary-600',
    overdue: 'bg-secondary-700 text-white',
};

function formatThaiDate(iso: string): string {
    return new Date(iso).toLocaleDateString('th-TH', { year: 'numeric', month: 'long', day: 'numeric' });
}

const CountdownBadge: React.FC<{ deadline: FilingDeadline }> = ({ deadline }) => {
    const tone = toneFor(deadline);
    return (
        <div className="space-y-1.5">
            <span className={clsx('inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold', TONE_BADGE[tone])}>
                <Clock size={12} />
                {deadline.is_overdue
                    ? `เลยกำหนดมาแล้ว ${Math.abs(deadline.days_remaining)} วัน`
                    : `เหลือ ${deadline.days_remaining} วัน`}
            </span>
            {tone === 'overdue' && (
                <p className="text-xs text-secondary-700 font-medium leading-relaxed">
                    เกินกำหนดยื่นแล้ว อาจมีเบี้ยปรับและเงินเพิ่มตามกฎหมาย
                </p>
            )}
        </div>
    );
};

const FormPicker: React.FC<FormPickerProps> = ({ forms, selected, onSelect }) => {
    return (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {forms.map((form) => {
                const meta = FORM_META[form.form_type];
                const isSelected = form.form_type === selected;
                return (
                    <button
                        key={form.form_type}
                        type="button"
                        onClick={() => onSelect(form.form_type)}
                        aria-pressed={isSelected}
                        className={clsx(
                            'print:hidden text-left rounded-xl border-2 p-5 shadow-sm transition-colors',
                            isSelected
                                ? 'border-primary-600 bg-primary-50'
                                : 'border-slate-200 bg-white hover:border-primary-200'
                        )}
                    >
                        <div className="flex items-start justify-between gap-3">
                            <div>
                                <h3 className="text-lg font-bold text-slate-900">{meta.name}</h3>
                                <p className="text-sm text-slate-500 mt-0.5">{meta.covers}</p>
                            </div>
                            {isSelected && (
                                <span className="flex-shrink-0 px-2 py-0.5 rounded-full text-[11px] font-semibold bg-primary-600 text-white">
                                    เลือกอยู่
                                </span>
                            )}
                        </div>

                        <div className="mt-4 flex items-center gap-2 text-sm text-slate-600">
                            <Calendar size={15} className="text-slate-400" />
                            กำหนดยื่น {formatThaiDate(form.deadline.deadline_date)}
                        </div>

                        <div className="mt-3">
                            <CountdownBadge deadline={form.deadline} />
                        </div>
                    </button>
                );
            })}
        </div>
    );
};

export default FormPicker;
