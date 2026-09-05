export interface DashboardStats {
  total_deductible: number;
  total_documents: number;
  verified_count: number;
}

export interface StatusBreakdown {
  verified: number;
  needs_review: number;
  rejected: number;
  not_deductible: number;
}

export interface RecentTransaction {
  id: string;
  merchant_name: string;
  transaction_date: string;
  total_amount: number;
  deductible_amount: number;
  status: string;
  created_at: string;
  receipt_image_url?: string;
  category?: string;
  ai_reasoning?: string;
}

export interface CategoryBreakdown {
  [category: string]: {
    total_deductible: number;
    max_limit: number;
    remaining: number;
  };
}

export interface DashboardSummary {
  total_deductible_amount: number;
  total_transactions: number;
  status_breakdown: StatusBreakdown;
  recent_transactions: RecentTransaction[];
  category_breakdown: CategoryBreakdown;
}

export interface DashboardStatsResponse {
  success: boolean;
  data: DashboardStats;
}

export interface DashboardSummaryResponse {
  success: boolean;
  data: DashboardSummary;
}

// --- UI-facing transaction/summary-card shapes (moved from data/mockData.ts) ---

export interface Transaction {
  id: string;
  date: string;
  merchant: string;
  category: string;
  amount: number;
  status: 'Verified' | 'Processing' | 'Needs Review' | 'Not Deductible';
  receiptUrl: string;
  aiReasoning: string;
  taxId?: string;
}

export interface SummaryStat {
  label: string;
  value: string;
  subValue?: string;
  trend?: 'up' | 'down' | 'neutral';
  color: 'blue' | 'green' | 'emerald' | 'slate';
}

// --- Income sync (/income/sync) ---

export interface PlatformTotal {
  gross_amount: number;
  fee: number;
  net_amount: number;
  record_count: number;
}

export interface IncomePlatformTotals {
  [platform: string]: PlatformTotal;
}

export interface TaxBracketBreakdown {
  bracket_min: number;
  bracket_max: number | null;
  rate: number;
  taxable_at_rate: number;
  tax_for_bracket: number;
}

export interface TaxEstimate {
  taxable_income: number;
  tax_due: number;
  brackets_verified: boolean;
  breakdown: TaxBracketBreakdown[];
}

export interface DeductionSuggestion {
  category_name: string;
  top_up_amount: number;
  marginal_rate: number;
  estimated_tax_saving: number;
  rule_reference: string;
}

export interface IncomeSyncResponse {
  success: boolean;
  period: string;
  platform_totals: IncomePlatformTotals;
  grand_total: PlatformTotal;
  tax_estimate: TaxEstimate;
  deduction_suggestions: DeductionSuggestion[];
}
