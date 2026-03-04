// Shared types matching backend schemas

export interface User {
  id: number;
  email: string;
  full_name: string;
  role: "admin" | "manager" | "staff";
  is_active: boolean;
  created_at: string;
}

export interface Restaurant {
  id: number;
  name: string;
  address: string;
  city: string;
  state: string;
  zip_code: string;
  phone: string;
  timezone: string;
  currency: string;
}

export interface AgentConfig {
  id: number;
  agent_name: string;
  autonomy_level: "full" | "semi" | "human_required";
  thresholds_json: Record<string, unknown> | null;
  is_active: boolean;
}

export interface AgentAction {
  id: number;
  agent_name: string;
  action_type: string;
  description: string;
  status: string;
  confidence: number | null;
  requires_approval: boolean;
  created_at: string;
}

export interface Invoice {
  id: number;
  vendor_id: number | null;
  invoice_number: string;
  date: string;
  due_date: string | null;
  total: number;
  status: "pending" | "approved" | "paid" | "rejected";
  ocr_confidence: number | null;
  created_at: string;
}

export interface GLEntry {
  id: number;
  account_id: number;
  date: string;
  debit: number;
  credit: number;
  description: string;
  source_type: string | null;
}

export interface InventoryItem {
  id: number;
  name: string;
  category: string;
  unit: string;
  current_stock: number;
  par_level: number;
  cost_per_unit: number;
  location: string | null;
}

export interface Vendor {
  id: number;
  name: string;
  contact_email: string | null;
  reliability_score: number;
  is_active: boolean;
}

export interface PurchaseOrder {
  id: number;
  vendor_id: number | null;
  status: "draft" | "submitted" | "delivered" | "cancelled";
  total: number;
  order_date: string;
  delivery_date: string | null;
  auto_generated: boolean;
}

export interface Employee {
  id: number;
  name: string;
  email: string | null;
  role: string;
  hourly_rate: number;
  status: "active" | "inactive" | "terminated";
  hire_date: string | null;
}

export interface GuestProfile {
  id: number;
  name: string | null;
  email: string | null;
  clv: number;
  churn_risk_score: number;
  visit_count: number;
  last_visit: string | null;
}

export interface Equipment {
  id: number;
  name: string;
  type: string;
  location: string | null;
  health_score: number;
  status: "operational" | "warning" | "critical" | "offline";
  last_service: string | null;
}

export interface Review {
  id: number;
  platform: string;
  rating: number | null;
  text: string | null;
  sentiment_score: number | null;
  response_status: "pending" | "drafted" | "approved" | "sent";
  author_name: string | null;
  review_date: string | null;
}

export interface Campaign {
  id: number;
  name: string;
  type: "email" | "sms" | "push" | "social";
  status: "draft" | "scheduled" | "active" | "completed" | "cancelled";
  sent_count: number;
  open_rate: number | null;
  conversion_rate: number | null;
}

export interface Location {
  id: number;
  name: string;
  city: string | null;
  region: string | null;
  is_active: boolean;
}

export interface LocationMetric {
  id: number;
  location_id: number;
  date: string;
  food_cost_pct: number | null;
  labor_cost_pct: number | null;
  net_margin: number | null;
  guest_score: number | null;
  revenue: number | null;
}

export interface Scenario {
  id: number;
  name: string;
  description: string | null;
  scenario_type: string;
  created_at: string;
}

export interface Alert {
  id: number;
  module: string;
  severity: "info" | "warning" | "critical";
  title: string;
  message: string;
  is_read: boolean;
  created_at: string;
}

export interface KPISnapshot {
  metric_name: string;
  value: number;
  previous_value: number | null;
  target_value: number | null;
}

export interface Forecast {
  id: number;
  forecast_type: string;
  target_date: string;
  predicted_value: number;
  confidence_lower: number | null;
  confidence_upper: number | null;
  actual_value: number | null;
}
