// Mirrors backend/app/services/filing_pack.py + filing_box_map.py exactly.
// See app/api/v1/endpoints/filing.py for the {success, data} envelope shape.

export type FormType = 'PND94' | 'PND90';

export interface PlatformTotal {
  gross_amount: number;
  fee: number;
  net_amount: number;
  record_count: number;
}

export interface IncomeAggregate {
  seller_id: string;
  period: string;
  platform_totals: Record<string, PlatformTotal>;
  grand_total: PlatformTotal;
}

export interface ExpenseMethodResult {
  expense_deduction: number;
  taxable_income: number;
  tax_due: number;
}

export interface ExpenseComparison {
  flat: ExpenseMethodResult;
  actual: ExpenseMethodResult;
  cheaper_method: 'flat' | 'actual';
  baht_difference: number;
  // Non-null only when cheaper_method is 'actual' -- the actual-expense
  // method needs documented receipts to survive an audit (filing_pack.py).
  recordkeeping_warning: string | null;
  documented_expenses: number;
  documented_expenses_source: 'none_recorded' | string;
}

export interface DeductionCategoryHeadroom {
  category_name: string;
  rule_id: string;
  max_limit: number;
  used: number;
  remaining: number;
}

export interface DeductionsSection {
  categories: DeductionCategoryHeadroom[];
  total_allowances_used: number;
  note: string;
}

export interface TaxBracketBreakdown {
  bracket_min: number;
  bracket_max: number | null;
  rate: number;
  taxable_at_rate: number;
  tax_for_bracket: number;
}

export interface TaxDue {
  taxable_income: number;
  tax_due: number;
  brackets_verified: boolean;
  breakdown: TaxBracketBreakdown[];
}

export interface BoxMappingRow {
  label_th: string;
  label_en: string;
  form_item: string;
  value: number;
  // Sourcing/citation text -- filing_box_map.py does not expose a separate
  // source_page field through this endpoint; the page/citation detail
  // already lives inside this note string.
  note: string;
}

export interface FilingDeadline {
  form_type: FormType;
  deadline_date: string;
  online_deadline_date: string | null;
  days_remaining: number;
  is_overdue: boolean;
}

export interface VerificationStatus {
  brackets_verified: boolean;
  tax_constants_verified: boolean;
  unverified: boolean;
}

export interface FilingPack {
  user_id: string;
  form_type: FormType;
  tax_year: number;
  income: IncomeAggregate;
  expense_comparison: ExpenseComparison;
  deductions: DeductionsSection;
  tax_due: TaxDue;
  box_mapping: BoxMappingRow[];
  document_checklist: string[];
  deadline: FilingDeadline;
  disclaimer: string;
  // Backend nests the unverified flag inside verification_status -- there
  // is no separate top-level `unverified` field (filing_pack.py).
  verification_status: VerificationStatus;
}

export interface FilingPackResponse {
  success: boolean;
  data: FilingPack;
}

export interface FilingFormSummary {
  form_type: FormType;
  covers_period: { date_from: string; date_to: string };
  deadline: FilingDeadline;
}

export interface FilingFormsData {
  tax_year: number;
  forms: FilingFormSummary[];
}

export interface FilingFormsResponse {
  success: boolean;
  data: FilingFormsData;
}
