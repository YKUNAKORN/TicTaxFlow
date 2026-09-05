import React, { useEffect, useState } from 'react';
import { Printer } from 'lucide-react';
import { filingApi } from '../api/filing';
import { storage } from '../lib/storage';
import UnverifiedBanner from '../components/filing/UnverifiedBanner';
import FormPicker from '../components/filing/FormPicker';
import ExpenseComparison from '../components/filing/ExpenseComparison';
import BoxMappingTable from '../components/filing/BoxMappingTable';
import DeductionSummary from '../components/filing/DeductionSummary';
import DocumentChecklist from '../components/filing/DocumentChecklist';
import type { FilingFormSummary, FilingPack, FormType } from '../types/filing';

const FORM_NAME: Record<FormType, string> = {
    PND94: 'ภ.ง.ด.94',
    PND90: 'ภ.ง.ด.90',
};

function formatThaiDate(iso: string): string {
    return new Date(iso).toLocaleDateString('th-TH', { year: 'numeric', month: 'long', day: 'numeric' });
}

const FilingPage: React.FC = () => {
    const [forms, setForms] = useState<FilingFormSummary[]>([]);
    const [taxYear, setTaxYear] = useState<number | null>(null);
    const [selectedForm, setSelectedForm] = useState<FormType>('PND94');

    const [pack, setPack] = useState<FilingPack | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [isRefreshing, setIsRefreshing] = useState(false);
    const [error, setError] = useState<string>('');

    useEffect(() => {
        fetchForms();
    }, []);

    useEffect(() => {
        if (taxYear !== null) {
            // Switching forms after the first load should refresh in place
            // (isRefreshing), not blank the whole page behind the full-page
            // spinner -- the form picker itself must stay visible to click.
            fetchPack(selectedForm, taxYear, pack !== null);
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [selectedForm, taxYear]);

    const fetchForms = async () => {
        const token = storage.getToken();
        if (!token) {
            setError('User not logged in');
            setIsLoading(false);
            return;
        }

        try {
            const response = await filingApi.getForms();
            if (response.success) {
                setForms(response.data.forms);
                setTaxYear(response.data.tax_year);
            }
        } catch (err: any) {
            console.error('ERROR: Failed to fetch filing forms:', err);
            setError(err?.message || 'Failed to load filing forms');
            setIsLoading(false);
        }
    };

    const fetchPack = async (formType: FormType, year: number, silent = false) => {
        if (silent) {
            setIsRefreshing(true);
        } else {
            setIsLoading(true);
        }
        setError('');

        try {
            const response = await filingApi.preview(formType, year);
            if (response.success) {
                setPack(response.data);
            }
        } catch (err: any) {
            console.error('ERROR: Failed to build filing pack:', err);
            setError(err?.message || 'Failed to load filing pack');
        } finally {
            setIsLoading(false);
            setIsRefreshing(false);
        }
    };

    if (isLoading) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
                    <p className="text-slate-600">กำลังเตรียมข้อมูลยื่นภาษี...</p>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="space-y-6">
                <div>
                    <h2 className="text-2xl font-bold text-slate-900">เตรียมยื่นภาษี</h2>
                    <p className="text-slate-500 mt-1">รวมรายได้ เปรียบเทียบวิธีหักค่าใช้จ่าย และเตรียมตัวเลขสำหรับยื่นแบบ</p>
                </div>
                <div className="bg-red-50 border border-red-200 rounded-lg p-6">
                    <h3 className="text-sm font-medium text-red-800">ไม่สามารถโหลดข้อมูลได้</h3>
                    <p className="mt-2 text-sm text-red-700">{error}</p>
                    <button
                        onClick={() => (taxYear !== null ? fetchPack(selectedForm, taxYear) : fetchForms())}
                        className="mt-4 px-4 py-2 bg-red-100 text-red-800 text-sm font-medium rounded-lg hover:bg-red-200 transition-colors"
                    >
                        ลองอีกครั้ง
                    </button>
                </div>
            </div>
        );
    }

    const unverified = pack?.verification_status.unverified ?? false;

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between flex-wrap gap-3">
                <div>
                    <h2 className="text-2xl font-bold text-slate-900">เตรียมยื่นภาษี</h2>
                    <p className="text-slate-500 mt-1">
                        {pack ? `${FORM_NAME[pack.form_type]} · ปีภาษี ${pack.tax_year} · กำหนดยื่น ${formatThaiDate(pack.deadline.deadline_date)}` : 'รวมรายได้ เปรียบเทียบวิธีหักค่าใช้จ่าย และเตรียมตัวเลขสำหรับยื่นแบบ'}
                    </p>
                </div>
                <button
                    onClick={() => window.print()}
                    className="print:hidden flex items-center gap-2 px-4 py-2 bg-primary-600 text-white font-medium rounded-lg hover:bg-primary-700 transition-colors"
                >
                    <Printer size={16} />
                    พิมพ์เอกสาร
                </button>
            </div>

            {unverified && <UnverifiedBanner />}

            <div className={unverified ? 'opacity-60 print:opacity-100 space-y-6' : 'space-y-6'}>
                <FormPicker forms={forms} selected={selectedForm} onSelect={setSelectedForm} />

                {isRefreshing && <p className="text-sm text-slate-400">กำลังอัปเดต...</p>}

                {pack && (
                    <>
                        <ExpenseComparison comparison={pack.expense_comparison} />

                        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                            <DeductionSummary deductions={pack.deductions} />
                            <DocumentChecklist items={pack.document_checklist} />
                        </div>

                        <BoxMappingTable rows={pack.box_mapping} />

                        <div className="bg-white rounded-xl p-6 shadow-sm border border-slate-200">
                            <p className="text-xs text-slate-400 leading-relaxed">{pack.disclaimer}</p>
                        </div>
                    </>
                )}
            </div>
        </div>
    );
};

export default FilingPage;
