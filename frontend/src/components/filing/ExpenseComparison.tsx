import React from 'react';
import { CheckCircle2, FileQuestion, ShieldAlert } from 'lucide-react';
import { clsx } from 'clsx';
import type { ExpenseComparison as ExpenseComparisonType } from '../../types/filing';

interface ExpenseComparisonProps {
    comparison: ExpenseComparisonType;
}

const METHOD_LABEL: Record<'flat' | 'actual', string> = {
    flat: 'หักเหมา',
    actual: 'หักตามจริง',
};

const MethodColumn: React.FC<{
    method: 'flat' | 'actual';
    result: { expense_deduction: number; taxable_income: number; tax_due: number };
    isRecommended: boolean;
    emptyState?: React.ReactNode;
}> = ({ method, result, isRecommended, emptyState }) => (
    <div
        className={clsx(
            'rounded-xl border-2 p-5 relative',
            isRecommended ? 'border-primary-600 bg-primary-50/40' : 'border-slate-200 bg-white'
        )}
    >
        {isRecommended && (
            <span className="absolute -top-3 left-4 px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-primary-600 text-white">
                แนะนำ
            </span>
        )}
        <h4 className="text-base font-bold text-slate-900">{METHOD_LABEL[method]}</h4>

        {emptyState ? (
            emptyState
        ) : (
            <dl className="mt-4 space-y-2.5 text-sm">
                <div className="flex justify-between">
                    <dt className="text-slate-500">หักค่าใช้จ่าย</dt>
                    <dd className="font-medium text-slate-900">฿{result.expense_deduction.toLocaleString()}</dd>
                </div>
                <div className="flex justify-between">
                    <dt className="text-slate-500">เงินได้สุทธิ</dt>
                    <dd className="font-medium text-slate-900">฿{result.taxable_income.toLocaleString()}</dd>
                </div>
                <div className="flex justify-between border-t border-slate-200 pt-2.5">
                    <dt className="text-slate-600 font-medium">ภาษีที่ต้องชำระ</dt>
                    <dd className="font-bold text-slate-900">฿{result.tax_due.toLocaleString()}</dd>
                </div>
            </dl>
        )}
    </div>
);

const ExpenseComparison: React.FC<ExpenseComparisonProps> = ({ comparison }) => {
    const noDocumentedExpenses = comparison.documented_expenses_source === 'none_recorded';
    const requiresRecords = comparison.cheaper_method === 'actual' && !!comparison.recordkeeping_warning;

    return (
        <div className="bg-white rounded-xl p-6 shadow-sm border border-slate-200">
            <h3 className="font-semibold text-slate-900 mb-1">เปรียบเทียบวิธีหักค่าใช้จ่าย</h3>
            <p className="text-sm text-slate-500 mb-6">หักเหมา 60% ของรายได้ เทียบกับหักค่าใช้จ่ายจริงตามเอกสาร</p>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <MethodColumn
                    method="flat"
                    result={comparison.flat}
                    isRecommended={comparison.cheaper_method === 'flat'}
                />
                <MethodColumn
                    method="actual"
                    result={comparison.actual}
                    isRecommended={comparison.cheaper_method === 'actual'}
                    emptyState={
                        noDocumentedExpenses ? (
                            <div className="mt-4 py-6 text-center">
                                <FileQuestion size={24} className="mx-auto mb-2 text-slate-300" />
                                <p className="text-sm font-medium text-slate-600">ยังไม่มีข้อมูลค่าใช้จ่ายทางธุรกิจที่บันทึกไว้</p>
                                <p className="text-xs text-slate-400 mt-1">ตัวเลข ฿0 ด้านล่างคือค่าเริ่มต้น ไม่ใช่ค่าที่คำนวณจากเอกสารจริง</p>
                            </div>
                        ) : undefined
                    }
                />
            </div>

            {requiresRecords && (
                <div className="mt-4 flex items-start gap-2 rounded-lg bg-accent-50 border border-accent-100 px-4 py-3">
                    <ShieldAlert size={16} className="flex-shrink-0 mt-0.5 text-accent-600" />
                    <p className="text-xs text-slate-700 leading-relaxed">{comparison.recordkeeping_warning}</p>
                </div>
            )}

            <div className="mt-6 pt-6 border-t border-slate-100">
                {comparison.baht_difference > 0 ? (
                    <p className="text-2xl sm:text-3xl font-bold text-slate-900 leading-snug flex items-center gap-2 flex-wrap">
                        <CheckCircle2 size={26} className="text-primary-600" />
                        เลือก{METHOD_LABEL[comparison.cheaper_method]}
                        ประหยัดภาษีได้{' '}
                        <span className="text-primary-600">฿{comparison.baht_difference.toLocaleString()}</span>
                    </p>
                ) : (
                    <p className="text-xl font-semibold text-slate-700">
                        ทั้งสองวิธีให้ภาษีเท่ากัน — แนะนำ{METHOD_LABEL[comparison.cheaper_method]} เพราะไม่ต้องเก็บเอกสารเพิ่ม
                    </p>
                )}
            </div>
        </div>
    );
};

export default ExpenseComparison;
