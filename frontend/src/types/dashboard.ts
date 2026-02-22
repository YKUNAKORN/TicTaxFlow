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
