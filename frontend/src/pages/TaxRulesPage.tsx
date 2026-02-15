import React from 'react';
import { BookOpen } from 'lucide-react';

const TaxRulesPage: React.FC = () => {
    return (
        <div className="flex flex-col items-center justify-center min-h-[60vh] text-center">
            <div className="h-16 w-16 bg-emerald-50 rounded-full flex items-center justify-center mb-6">
                <BookOpen size={32} className="text-emerald-500" />
            </div>
            <h2 className="text-2xl font-bold text-slate-900 mb-2">Tax Rules Library</h2>
            <p className="text-slate-500 max-w-md">
                AI-powered documentation and search for Thai Revenue Department regulations.
            </p>
        </div>
    );
};

export default TaxRulesPage;
