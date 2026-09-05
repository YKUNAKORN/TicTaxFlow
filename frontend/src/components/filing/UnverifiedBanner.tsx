import React from 'react';
import { AlertTriangle } from 'lucide-react';

const UnverifiedBanner: React.FC = () => (
    <div
        role="alert"
        className="flex items-start gap-3 rounded-xl border-2 border-accent-500 bg-accent-50 px-5 py-4 shadow-sm"
    >
        <AlertTriangle size={22} className="flex-shrink-0 mt-0.5 text-accent-600" />
        <p className="text-sm font-semibold text-slate-900 leading-relaxed">
            ตัวเลขในหน้านี้ยังไม่ได้ยืนยันกับกรมสรรพากร — ห้ามนำไปใช้ยื่นจริง
        </p>
    </div>
);

export default UnverifiedBanner;
