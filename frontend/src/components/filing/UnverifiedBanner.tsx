import React from 'react';
import { AlertTriangle } from 'lucide-react';

const UnverifiedBanner: React.FC = () => (
    <div
        role="alert"
        className="flex items-start gap-3 rounded-xl border-2 border-accent-500 bg-accent-50 px-5 py-4 shadow-sm"
    >
        <AlertTriangle size={22} className="flex-shrink-0 mt-0.5 text-accent-600" />
        <p className="text-sm font-semibold text-slate-900 leading-relaxed">
            The figures on this page have not been verified against the Revenue Department — do not use them for an actual filing.
        </p>
    </div>
);

export default UnverifiedBanner;
