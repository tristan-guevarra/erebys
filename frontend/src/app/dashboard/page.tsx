"use client";

import { useOverviewKPIs, useRevenueByDay } from "@/hooks/use-data";
import { KPICard } from "@/components/ui/kpi-card";
import { PageHeader, Card, PageLoader } from "@/components/ui/shared";
import { RevenueChart, BookingsChart } from "@/components/charts";
import { formatCurrency, formatNumber } from "@/lib/utils";
import {
  DollarSign,
  CalendarCheck,
  Target,
  AlertTriangle,
  Users,
  Heart,
  XCircle,
} from "lucide-react";

export default function DashboardPage() {
  const { data: kpis, isLoading: kpiLoading } = useOverviewKPIs(30);
  const { data: revenue, isLoading: revLoading } = useRevenueByDay(30);

  if (kpiLoading) return <PageLoader />;

  return (
    <div className="space-y-6 animate-fade-in">
      <PageHeader
        title="Revenue Intelligence"
        description="30-day performance overview across all events"
      />

      {/* kpi grid */}
      <div className="grid grid-cols-2 lg:grid-cols-4 xl:grid-cols-7 gap-4">
        <KPICard
          title="Revenue"
          value={formatCurrency(kpis?.total_revenue ?? 0)}
          change={kpis?.revenue_change}
          icon={<DollarSign className="w-4 h-4" />}
          variant="success"
          className="stagger-1 animate-slide-up"
        />
        <KPICard
          title="Bookings"
          value={formatNumber(kpis?.total_bookings ?? 0)}
          change={kpis?.bookings_change}
          icon={<CalendarCheck className="w-4 h-4" />}
          className="stagger-2 animate-slide-up"
        />
        <KPICard
          title="Utilization"
          value={`${kpis?.utilization_rate?.toFixed(1) ?? 0}%`}
          change={kpis?.utilization_change}
          icon={<Target className="w-4 h-4" />}
          className="stagger-3 animate-slide-up"
        />
        <KPICard
          title="No-Show Rate"
          value={`${kpis?.no_show_rate?.toFixed(1) ?? 0}%`}
          change={kpis?.no_show_change}
          icon={<AlertTriangle className="w-4 h-4" />}
          variant={(kpis?.no_show_rate ?? 0) > 15 ? "danger" : "default"}
          className="stagger-4 animate-slide-up"
        />
        <KPICard
          title="Active Athletes"
          value={formatNumber(kpis?.active_athletes ?? 0)}
          change={kpis?.athletes_change}
          icon={<Users className="w-4 h-4" />}
          className="stagger-5 animate-slide-up"
        />
        <KPICard
          title="Avg LTV"
          value={formatCurrency(kpis?.avg_ltv ?? 0)}
          change={kpis?.ltv_change}
          icon={<Heart className="w-4 h-4" />}
          className="stagger-6 animate-slide-up"
        />
        <KPICard
          title="Cancel Rate"
          value={`${kpis?.cancellation_rate?.toFixed(1) ?? 0}%`}
          change={kpis?.cancellation_change}
          icon={<XCircle className="w-4 h-4" />}
          variant={(kpis?.cancellation_rate ?? 0) > 10 ? "warning" : "default"}
          className="stagger-6 animate-slide-up"
        />
      </div>

      {/* charts */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <Card title="Revenue Trend" className="lg:col-span-2">
          {revLoading ? (
            <PageLoader />
          ) : (
            <RevenueChart data={revenue ?? []} />
          )}
        </Card>

        <Card title="Daily Bookings">
          {revLoading ? (
            <PageLoader />
          ) : (
            <BookingsChart data={revenue ?? []} />
          )}
        </Card>
      </div>

      {/* quick stats row */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card title="Performance Alerts">
          <div className="space-y-3">
            {(kpis?.no_show_rate ?? 0) > 15 && (
              <div className="flex items-start gap-3 p-3 rounded-lg bg-rose-500/5 border border-rose-500/10">
                <AlertTriangle className="w-4 h-4 text-accent-rose mt-0.5 shrink-0" />
                <div>
                  <p className="text-sm font-medium">High No-Show Rate</p>
                  <p className="text-xs text-[var(--text-secondary)] mt-0.5">
                    {kpis?.no_show_rate?.toFixed(1)}% — consider requiring deposits
                    or sending reminders.
                  </p>
                </div>
              </div>
            )}
            {(kpis?.utilization_rate ?? 100) < 50 && (
              <div className="flex items-start gap-3 p-3 rounded-lg bg-amber-500/5 border border-amber-500/10">
                <Target className="w-4 h-4 text-accent-amber mt-0.5 shrink-0" />
                <div>
                  <p className="text-sm font-medium">Low Utilization</p>
                  <p className="text-xs text-[var(--text-secondary)] mt-0.5">
                    {kpis?.utilization_rate?.toFixed(1)}% capacity filled — review
                    pricing or increase marketing.
                  </p>
                </div>
              </div>
            )}
            {(kpis?.no_show_rate ?? 0) <= 15 &&
              (kpis?.utilization_rate ?? 0) >= 50 && (
                <div className="flex items-start gap-3 p-3 rounded-lg bg-emerald-500/5 border border-emerald-500/10">
                  <Target className="w-4 h-4 text-accent-emerald mt-0.5 shrink-0" />
                  <div>
                    <p className="text-sm font-medium">All Systems Healthy</p>
                    <p className="text-xs text-[var(--text-secondary)] mt-0.5">
                      No critical alerts at this time.
                    </p>
                  </div>
                </div>
              )}
          </div>
        </Card>

        <Card title="Quick Metrics" className="md:col-span-2">
          <div className="grid grid-cols-2 gap-4">
            <div className="p-3 rounded-lg bg-[var(--bg-secondary)]">
              <p className="text-xs text-[var(--text-muted)] mb-1">Revenue per Booking</p>
              <p className="font-display text-lg font-bold">
                {formatCurrency(
                  (kpis?.total_revenue ?? 0) /
                    Math.max(kpis?.total_bookings ?? 1, 1)
                )}
              </p>
            </div>
            <div className="p-3 rounded-lg bg-[var(--bg-secondary)]">
              <p className="text-xs text-[var(--text-muted)] mb-1">Est. Monthly Revenue</p>
              <p className="font-display text-lg font-bold">
                {formatCurrency((kpis?.total_revenue ?? 0))}
              </p>
            </div>
            <div className="p-3 rounded-lg bg-[var(--bg-secondary)]">
              <p className="text-xs text-[var(--text-muted)] mb-1">Lost to No-Shows</p>
              <p className="font-display text-lg font-bold text-accent-rose">
                {formatCurrency(
                  ((kpis?.total_revenue ?? 0) * (kpis?.no_show_rate ?? 0)) / 100
                )}
              </p>
            </div>
            <div className="p-3 rounded-lg bg-[var(--bg-secondary)]">
              <p className="text-xs text-[var(--text-muted)] mb-1">Capacity Opportunity</p>
              <p className="font-display text-lg font-bold text-accent-amber">
                {(100 - (kpis?.utilization_rate ?? 0)).toFixed(0)}% unfilled
              </p>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}
