export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  per_page: number;
  pages: number;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface NLQueryResponse {
  query: string;
  answer: string;
  data?: Record<string, unknown>;
}

export interface ReputationScore {
  avg_rating: number;
  total_reviews: number;
  avg_sentiment: number;
}

export interface LaborTracker {
  current_labor_pct: number;
  target_labor_pct: number;
  total_labor_cost: number;
  total_sales: number;
  staff_on_clock: number;
}

export interface VisionStats {
  active_alerts: number;
  waste_today: number;
  waste_cost_today: number;
  compliance_score: number;
}

export interface PLReport {
  revenue: number;
  cost_of_goods: number;
  gross_profit: number;
  labor_cost: number;
  operating_expenses: number;
  net_income: number;
  period: string;
}

export interface CashFlowForecast {
  date: string;
  projected_balance: number;
  inflows: number;
  outflows: number;
}

export interface AccuracyMetrics {
  overall_accuracy: number;
  sales_accuracy: number;
  item_accuracy: number;
  labor_accuracy: number;
  model_version: string;
  last_retrained: string;
}
