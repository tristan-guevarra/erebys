export interface User {
  id: string;
  email: string;
  full_name: string;
  is_active: boolean;
  is_superadmin: boolean;
  org_roles: OrgRole[];
}

export interface OrgRole {
  organization_id: string;
  role: "superadmin" | "admin" | "manager";
  organization_name?: string;
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: User;
}

export interface Organization {
  id: string;
  name: string;
  slug: string;
  sport_type: string;
  region: string;
  competition_proxy: number;
  logo_url?: string;
}

export type EventType = "camp" | "clinic" | "private";
export type EventStatus = "draft" | "published" | "full" | "completed" | "cancelled";

export interface Event {
  id: string;
  organization_id: string;
  coach_id?: string;
  title: string;
  description?: string;
  event_type: EventType;
  status: EventStatus;
  capacity: number;
  booked_count: number;
  base_price: number;
  current_price: number;
  start_date: string;
  end_date?: string;
  start_time: string;
  end_time: string;
  location?: string;
  skill_level: string;
  created_at: string;
}

export type BookingStatus = "confirmed" | "cancelled" | "waitlisted" | "pending";

export interface Booking {
  id: string;
  event_id: string;
  athlete_id: string;
  organization_id: string;
  status: BookingStatus;
  source: string;
  price_paid: number;
  discount_applied: number;
  booked_at: string;
}

export interface OverviewKPIs {
  total_revenue: number;
  revenue_change: number;
  total_bookings: number;
  bookings_change: number;
  utilization_rate: number;
  utilization_change: number;
  no_show_rate: number;
  no_show_change: number;
  active_athletes: number;
  athletes_change: number;
  avg_ltv: number;
  ltv_change: number;
  cancellation_rate: number;
  cancellation_change: number;
}

export interface RevenueByDay {
  date: string;
  revenue: number;
  bookings: number;
}

export interface CohortRow {
  cohort_month: string;
  cohort_size: number;
  retention: number[];
}

export interface AthleteLTVBucket {
  bucket: string;
  count: number;
  total_ltv: number;
  avg_ltv: number;
}

export interface NoShowRisk {
  athlete_id: string;
  athlete_name: string;
  risk_score: number;
  risk_level: "low" | "medium" | "high";
  total_bookings: number;
  no_show_rate: number;
}

export interface EventPerformance {
  id: string;
  title: string;
  event_type: EventType;
  revenue: number;
  bookings: number;
  capacity: number;
  utilization_rate: number;
  no_show_rate: number;
  avg_rating: number;
  cancellation_rate: number;
}

export interface PricingRecommendation {
  id: string;
  event_id: string;
  current_price: number;
  suggested_price: number;
  confidence_score: number;
  price_change_pct: number;
  expected_demand_change: number;
  expected_revenue_change: number;
  explanation: string;
  drivers: Record<string, DriverInfo>;
  created_at: string;
}

export interface DriverInfo {
  value: string;
  impact: "upward" | "downward";
  weight: number;
  description: string;
}

export interface WhatIfResult {
  price: number;
  estimated_demand: number;
  estimated_revenue: number;
  estimated_utilization: number;
}

export interface PriceChangeRequest {
  id: string;
  event_id: string;
  old_price: number;
  new_price: number;
  status: "pending" | "approved" | "rejected" | "applied";
  reason?: string;
  created_at: string;
}

export interface Experiment {
  id: string;
  name: string;
  description?: string;
  status: "draft" | "running" | "paused" | "completed";
  variant_a_price: number;
  variant_b_price: number;
  traffic_split: number;
  start_date?: string;
  end_date?: string;
  results?: ExperimentResults;
  created_at: string;
}

export interface ExperimentResults {
  variant_a: { bookings: number; revenue: number; conversion_rate: number };
  variant_b: { bookings: number; revenue: number; conversion_rate: number };
  winner?: "A" | "B" | "inconclusive";
  lift_pct?: number;
}

export interface AuditLog {
  id: string;
  action: string;
  resource_type: string;
  resource_id?: string;
  details?: Record<string, unknown>;
  user_id?: string;
  created_at: string;
}

export interface FeatureFlag {
  id: string;
  feature_key: string;
  enabled: boolean;
}

export interface InsightReport {
  id: string;
  report_type: string;
  period_start: string;
  period_end: string;
  narrative: string;
  highlights?: Record<string, unknown>;
  alerts?: Record<string, unknown>;
  created_at: string;
}

export interface PlatformOverview {
  total_revenue_30d: number;
  active_academies: number;
  total_athletes: number;
  total_events_month: number;
  platform_utilization: number;
  mrr: number;
  revenue_growth_pct: number;
  total_pending_changes: number;
}

export interface AcademyMetrics {
  id: string;
  name: string;
  sport_type: string;
  region: string;
  monthly_revenue: number;
  active_athletes: number;
  events_count: number;
  utilization_rate: number;
  health_score: number;
  athlete_retention_rate: number;
  created_at: string;
}

export interface PlatformRevenueDay {
  date: string;
  total: number;
}

export interface PlatformUser {
  id: string;
  email: string;
  full_name: string;
  is_active: boolean;
  is_superadmin: boolean;
  created_at: string;
  orgs: { org_id: string; org_name: string; role: string }[];
}

export interface SystemHealth {
  db_status: string;
  db_pool_size: number;
  redis_status: string;
  celery_status: string;
  last_metrics_run: string | null;
  last_insight_run: string | null;
  api_version: string;
  uptime_status: string;
}

export interface EvaluationListItem {
  id: string;
  athlete_id: string;
  athlete_name: string;
  coach_id: string | null;
  coach_name: string | null;
  evaluation_type: string;
  period_start: string;
  period_end: string;
  overall_score: number;
  status: string;
  ai_generated: boolean;
  created_at: string;
  category_count: number;
}

export interface EvaluationTemplate {
  id: string;
  organization_id: string | null;
  sport_type: string;
  name: string;
  categories: { name: string; weight: number }[];
  is_default: boolean;
}
