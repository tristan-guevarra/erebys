"use client";

import {
  AreaChart,
  Area,
  BarChart,
  Bar,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";
import type { RevenueByDay, WhatIfResult, CohortRow, AthleteLTVBucket } from "@/types";

const CHART_COLORS = {
  blue: "#8b5cf6",
  cyan: "#06b6d4",
  emerald: "#10b981",
  amber: "#f59e0b",
  rose: "#f43f5e",
  purple: "#a78bfa",
};

const TOOLTIP_STYLE = {
  contentStyle: {
    background: "#18181F",
    border: "1px solid rgba(255,255,255,0.08)",
    borderRadius: "8px",
    fontSize: "12px",
    color: "#EDEDF0",
  },
  labelStyle: { color: "#94949F" },
};

export function RevenueChart({ data }: { data: RevenueByDay[] }) {
  return (
    <ResponsiveContainer width="100%" height={280}>
      <AreaChart data={data} margin={{ top: 5, right: 10, left: 0, bottom: 0 }}>
        <defs>
          <linearGradient id="revGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor={CHART_COLORS.blue} stopOpacity={0.3} />
            <stop offset="95%" stopColor={CHART_COLORS.blue} stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
        <XAxis
          dataKey="date"
          tick={{ fill: "#52525B", fontSize: 11 }}
          tickLine={false}
          axisLine={false}
        />
        <YAxis
          tick={{ fill: "#52525B", fontSize: 11 }}
          tickLine={false}
          axisLine={false}
          tickFormatter={(v) => `$${v >= 1000 ? `${(v / 1000).toFixed(0)}k` : v}`}
        />
        <Tooltip
          {...TOOLTIP_STYLE}
          formatter={(value: number) => [`$${value.toLocaleString()}`, "Revenue"]}
        />
        <Area
          type="monotone"
          dataKey="revenue"
          stroke={CHART_COLORS.blue}
          strokeWidth={2}
          fill="url(#revGrad)"
        />
      </AreaChart>
    </ResponsiveContainer>
  );
}

export function BookingsChart({ data }: { data: RevenueByDay[] }) {
  return (
    <ResponsiveContainer width="100%" height={200}>
      <BarChart data={data} margin={{ top: 5, right: 10, left: 0, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
        <XAxis dataKey="date" tick={{ fill: "#52525B", fontSize: 10 }} tickLine={false} axisLine={false} />
        <YAxis tick={{ fill: "#52525B", fontSize: 10 }} tickLine={false} axisLine={false} />
        <Tooltip {...TOOLTIP_STYLE} />
        <Bar dataKey="bookings" fill={CHART_COLORS.cyan} radius={[3, 3, 0, 0]} opacity={0.8} />
      </BarChart>
    </ResponsiveContainer>
  );
}

export function WhatIfChart({
  data,
  currentPrice,
}: {
  data: WhatIfResult[];
  currentPrice: number;
}) {
  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={data} margin={{ top: 5, right: 30, left: 0, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
        <XAxis
          dataKey="price"
          tick={{ fill: "#52525B", fontSize: 11 }}
          tickFormatter={(v) => `$${v}`}
        />
        <YAxis
          yAxisId="left"
          tick={{ fill: "#52525B", fontSize: 11 }}
          tickFormatter={(v) => `$${v >= 1000 ? `${(v / 1000).toFixed(1)}k` : v}`}
        />
        <YAxis
          yAxisId="right"
          orientation="right"
          tick={{ fill: "#52525B", fontSize: 11 }}
        />
        <Tooltip
          {...TOOLTIP_STYLE}
          formatter={(value: number, name: string) => {
            if (name === "Revenue") return [`$${value.toLocaleString()}`, name];
            return [value.toFixed(1), name];
          }}
        />
        <Legend wrapperStyle={{ fontSize: 11, color: "#94949F" }} />
        <Line
          yAxisId="left"
          type="monotone"
          dataKey="estimated_revenue"
          name="Revenue"
          stroke={CHART_COLORS.emerald}
          strokeWidth={2}
          dot={{ fill: CHART_COLORS.emerald, r: 4 }}
        />
        <Line
          yAxisId="right"
          type="monotone"
          dataKey="estimated_demand"
          name="Demand"
          stroke={CHART_COLORS.amber}
          strokeWidth={2}
          dot={{ fill: CHART_COLORS.amber, r: 4 }}
          strokeDasharray="5 5"
        />
      </LineChart>
    </ResponsiveContainer>
  );
}

// cohort heatmap (simplified table view)
export function CohortChart({ data }: { data: CohortRow[] }) {
  if (!data || data.length === 0) return null;

  const maxMonths = Math.max(...data.map((c) => c.retention.length));

  return (
    <div className="overflow-x-auto">
      <table className="text-xs w-full">
        <thead>
          <tr>
            <th className="px-3 py-2 text-left text-[var(--text-muted)] font-medium">
              Cohort
            </th>
            <th className="px-3 py-2 text-center text-[var(--text-muted)] font-medium">
              Size
            </th>
            {Array.from({ length: maxMonths }, (_, i) => (
              <th
                key={i}
                className="px-3 py-2 text-center text-[var(--text-muted)] font-medium"
              >
                M{i}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((row) => (
            <tr key={row.cohort_month}>
              <td className="px-3 py-1.5 font-mono text-[var(--text-secondary)]">
                {row.cohort_month}
              </td>
              <td className="px-3 py-1.5 text-center font-mono">
                {row.cohort_size}
              </td>
              {row.retention.map((pct, i) => {
                const intensity = Math.min(pct / 100, 1);
                const bg = `rgba(16, 185, 129, ${intensity * 0.5})`;
                return (
                  <td
                    key={i}
                    className="px-3 py-1.5 text-center font-mono"
                    style={{ background: bg }}
                  >
                    {pct.toFixed(0)}%
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export function LTVChart({ data }: { data: AthleteLTVBucket[] }) {
  return (
    <ResponsiveContainer width="100%" height={240}>
      <BarChart data={data} margin={{ top: 5, right: 10, left: 0, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
        <XAxis dataKey="bucket" tick={{ fill: "#52525B", fontSize: 10 }} tickLine={false} axisLine={false} />
        <YAxis tick={{ fill: "#52525B", fontSize: 10 }} tickLine={false} axisLine={false} />
        <Tooltip {...TOOLTIP_STYLE} />
        <Bar dataKey="count" name="Athletes" fill={CHART_COLORS.purple} radius={[4, 4, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}
