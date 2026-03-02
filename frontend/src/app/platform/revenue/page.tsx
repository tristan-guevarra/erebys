"use client";

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
} from "recharts";
import { PageLoader, Card, PageHeader } from "@/components/ui/shared";
import { usePlatformRevenue } from "@/hooks/use-platform";
function formatRevenue(n: number) {
  if (n >= 1000) return `$${(n / 1000).toFixed(1)}k`;
  return `$${n}`;
}

function shortDate(dateStr: string) {
  const d = new Date(dateStr);
  return `${d.getMonth() + 1}/${d.getDate()}`;
}

interface DailyTotal { date: string; total: number; }
interface OrgRevenue  { org_id: string; org_name: string; revenue: number; }
interface SportRevenue { sport_type: string; revenue: number; }

interface RevenueData {
  daily: DailyTotal[];
  by_org: OrgRevenue[];
  by_sport: SportRevenue[];
  period_days: number;
}

export default function RevenuePage() {
  const { data, isLoading } = usePlatformRevenue();

  if (isLoading) return <PageLoader />;

  const revenue = data as RevenueData | undefined;

  const dailyData = (revenue?.daily || []).map((d) => ({
    date: shortDate(d.date),
    total: d.total,
  }));

  const byOrgData = (revenue?.by_org || []).map((o) => ({
    name: o.org_name.length > 16 ? o.org_name.slice(0, 16) + "…" : o.org_name,
    value: o.revenue,
  }));

  const bySportData = (revenue?.by_sport || []).map((s) => ({
    name: s.sport_type,
    value: s.revenue,
  }));

  const tooltipStyle = {
    background: "var(--bg-card)",
    border: "1px solid var(--border-subtle)",
    borderRadius: "8px",
    color: "var(--text-primary)",
    fontSize: "12px",
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="Revenue Analytics"
        description="Platform-wide revenue breakdown over the last 30 days."
      />

      {/* daily revenue line chart */}
      <Card title="Daily Revenue (30 days)">
        {dailyData.length > 0 ? (
          <div style={{ height: 280 }}>
            <ResponsiveContainer width="100%" height="100%">
              <LineChart
                data={dailyData}
                margin={{ top: 8, right: 16, bottom: 0, left: 8 }}
              >
                <CartesianGrid
                  strokeDasharray="3 3"
                  stroke="rgba(91,124,250,0.08)"
                />
                <XAxis
                  dataKey="date"
                  tick={{ fill: "var(--text-muted)", fontSize: 11 }}
                  axisLine={false}
                  tickLine={false}
                />
                <YAxis
                  tick={{ fill: "var(--text-muted)", fontSize: 11 }}
                  axisLine={false}
                  tickLine={false}
                  tickFormatter={(v) => formatRevenue(v)}
                />
                <Tooltip
                  contentStyle={tooltipStyle}
                  formatter={(v: number) => [formatRevenue(v), "Revenue"]}
                />
                <Line
                  type="monotone"
                  dataKey="total"
                  stroke="var(--accent-cyan)"
                  strokeWidth={2}
                  dot={false}
                  activeDot={{ r: 4, fill: "var(--accent-cyan)" }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        ) : (
          <div className="py-12 text-center text-[var(--text-muted)]">
            No revenue data available.
          </div>
        )}
      </Card>

      <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
        {/* by org */}
        <Card title="Revenue by Academy">
          {byOrgData.length > 0 ? (
            <div style={{ height: 240 }}>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={byOrgData}
                  layout="vertical"
                  margin={{ top: 4, right: 16, bottom: 4, left: 8 }}
                >
                  <CartesianGrid
                    strokeDasharray="3 3"
                    stroke="rgba(91,124,250,0.08)"
                    horizontal={false}
                  />
                  <XAxis
                    type="number"
                    tick={{ fill: "var(--text-muted)", fontSize: 11 }}
                    axisLine={false}
                    tickLine={false}
                    tickFormatter={(v) => formatRevenue(v)}
                  />
                  <YAxis
                    type="category"
                    dataKey="name"
                    tick={{ fill: "var(--text-muted)", fontSize: 11 }}
                    axisLine={false}
                    tickLine={false}
                    width={100}
                  />
                  <Tooltip
                    contentStyle={tooltipStyle}
                    formatter={(v: number) => [formatRevenue(v), "Revenue"]}
                  />
                  <Bar
                    dataKey="value"
                    fill="var(--accent-cyan)"
                    radius={[0, 4, 4, 0]}
                    fillOpacity={0.85}
                  />
                </BarChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <div className="py-10 text-center text-[var(--text-muted)]">
              No data.
            </div>
          )}
        </Card>

        {/* by sport */}
        <Card title="Revenue by Sport">
          {bySportData.length > 0 ? (
            <div style={{ height: 240 }}>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={bySportData}
                  margin={{ top: 4, right: 16, bottom: 4, left: 8 }}
                >
                  <CartesianGrid
                    strokeDasharray="3 3"
                    stroke="rgba(91,124,250,0.08)"
                  />
                  <XAxis
                    dataKey="name"
                    tick={{ fill: "var(--text-muted)", fontSize: 11 }}
                    axisLine={false}
                    tickLine={false}
                  />
                  <YAxis
                    tick={{ fill: "var(--text-muted)", fontSize: 11 }}
                    axisLine={false}
                    tickLine={false}
                    tickFormatter={(v) => formatRevenue(v)}
                  />
                  <Tooltip
                    contentStyle={tooltipStyle}
                    formatter={(v: number) => [formatRevenue(v), "Revenue"]}
                  />
                  <Bar
                    dataKey="value"
                    fill="var(--accent-emerald)"
                    radius={[4, 4, 0, 0]}
                    fillOpacity={0.85}
                  />
                </BarChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <div className="py-10 text-center text-[var(--text-muted)]">
              No data.
            </div>
          )}
        </Card>
      </div>
    </div>
  );
}
