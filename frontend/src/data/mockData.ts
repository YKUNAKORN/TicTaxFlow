export interface Transaction {
    id: string;
    date: string;
    merchant: string;
    category: "Insurance" | "Donation" | "Investment" | "Shopping" | "Other";
    amount: number;
    status: "Verified" | "Processing" | "Needs Review";
    receiptUrl: string; // Analyze placeholder
    aiReasoning: string;
    taxId?: string;
}

export interface SummaryStat {
    label: string;
    value: string;
    subValue?: string;
    trend?: "up" | "down" | "neutral";
    color: "blue" | "green" | "emerald" | "slate";
}

export const mockSummaryStats: SummaryStat[] = [
    {
        label: "Total Deductions",
        value: "฿ 45,200",
        subValue: "+12% from last month",
        trend: "up",
        color: "blue",
    },
    {
        label: "SSF/RMF Allowance",
        value: "฿ 154,800",
        subValue: "Remaining of 200k limit",
        color: "green",
    },
    {
        label: "Documents Processed",
        value: "14",
        subValue: "All verified",
        trend: "neutral",
        color: "slate",
    },
];

export const mockTransactions: Transaction[] = [
    {
        id: "tx_1",
        date: "2025-01-24",
        merchant: "AIA Thailand",
        category: "Insurance",
        amount: 25000,
        status: "Verified",
        receiptUrl: "https://placehold.co/400x600/e2e8f0/1e293b?text=Receipt+Image",
        aiReasoning: "Matches Life Insurance premium deduction criteria (max 100k).",
        taxId: "0105555555555",
    },
    {
        id: "tx_2",
        date: "2025-01-22",
        merchant: "Unicef Thailand",
        category: "Donation",
        amount: 5000,
        status: "Verified",
        receiptUrl: "https://placehold.co/400x600/e2e8f0/1e293b?text=Donation+Receipt",
        aiReasoning: "E-Donation detected. Eligible for 2x deduction.",
        taxId: "0994000160000",
    },
    {
        id: "tx_3",
        date: "2025-01-20",
        merchant: "Central Department Store",
        category: "Shopping",
        amount: 12500,
        status: "Processing",
        receiptUrl: "https://placehold.co/400x600/e2e8f0/1e293b?text=Shopping+Bill",
        aiReasoning: "Analyzing for 'Easy E-Receipt' eligibility...",
        taxId: "0107536000000",
    },
    {
        id: "tx_4",
        date: "2025-01-15",
        merchant: "Starbucks Coffee",
        category: "Other",
        amount: 350,
        status: "Needs Review",
        receiptUrl: "https://placehold.co/400x600/e2e8f0/1e293b?text=Coffee+Receipt",
        aiReasoning: "Likely personal expense. Not tax deductible under current rules.",
        taxId: "0100000000000",
    },
    {
        id: "tx_5",
        date: "2025-01-10",
        merchant: "SCB Asset Management",
        category: "Investment",
        amount: 50000,
        status: "Verified",
        receiptUrl: "https://placehold.co/400x600/e2e8f0/1e293b?text=Fund+Purchase",
        aiReasoning: "SSF purchase confirmed. Within 30% income limit.",
        taxId: "0107536000000",
    },
];
