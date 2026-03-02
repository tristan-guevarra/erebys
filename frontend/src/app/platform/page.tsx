"use client";

import { PageLoader } from "@/components/ui/shared";
import { Card, PageHeader } from "@/components/ui/shared";
import { usePlatformOverview, usePlatformAcademies } from "@/hooks/use-platform";
import type { AcademyMetrics, PlatformOverview } from "@/types";

function formatRevenue(n: number) {
  if (n >= 1000) return `$${(n / 1000).toFixed(1)}k`;
  return `$${n}`;
}

function HealthBar({ score }: { score: number }) {
  const color =
    score >= 80
      ? "var(--accent-emerald)"
      : score >= 60
      ? "var(--accent-amber)"
      : "var(--accent-rose)";
  return (
    <div className="h-1.5 rounded-full bg-[var(--bg-secondary)] w-24">
      <div
        className="h-1.5 rounded-full"
        style={{ width: `${score}%`, background: color }}
      />
    </div>
  );
}

function HealthScoreLabel({ score }: { score: number }) {
  const color =
    score >= 80
      ? "var(--accent-emerald)"
      : score >= 60
      ? "var(--accent-amber)"
      : "var(--accent-rose)";
  return (
    <span className="text-sm font-mono font-semibold" style={{ color }}>
      {score}
    </span>
  );
}

function KPICard({
  label,
  value,
  sub,
}: {
  label: string;
  value: string | number;
  sub?: string;
}) {
  return (
    <div className="card-glass rounded-xl p-5">
      <p className="text-xs font-medium uppercase tracking-wider text-[var(--text-muted)] mb-1">
        {label}
      </p>
      <p
        className="font-display text-2xl font-bold"
        style={{ color: "var(--accent-cyan)" }}
      >
        {value}
      </p>
      {sub && (
        <p className="text-xs text-[var(--text-secondary)] mt-1">{sub}</p>
      )}
    </div>
  );
}

export default function PlatformOverviewPage() {
  const { data: overview, isLoading: overviewLoading, isError: overviewError } = usePlatformOverview();
  const { data: academies, isLoading: academiesLoading, isError: academiesError } = usePlatformAcademies();

  if (overviewLoading || academiesLoading) return <PageLoader />;

  if (overviewError || academiesError) {
    return (
      <div className="flex flex-col items-center justify-center py-24 gap-3">
        <p className="text-[var(--text-muted)] text-sm">Failed to load platform data.</p>
        <p className="text-[var(--text-muted)] text-xs">
          Check backend logs: <code className="font-mono text-[var(--accent-cyan)]">docker compose logs backend --tail=50</code>
        </p>
        <button
          onClick={() => window.location.reload()}
          className="btn-secondary text-xs mt-2"
        >
          Retry
        </button>
      </div>
    );
  }

  const kpis = overview as PlatformOverview | undefined;
  const academyList = (academies as AcademyMetrics[] | undefined) || [];

  const sorted = [...academyList].sort((a, b) => b.health_score - a.health_score);

  return (
    <div className="space-y-6">
      <PageHeader
        title="Platform Overview"
        description="Real-time metrics across all academies on the Erebys Intelligence Suite."
      />

      {/* kpi cards */}
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <KPICard
          label="Revenue (30d)"
          value={kpis ? formatRevenue(kpis.total_revenue_30d) : "—"}
          sub={kpis ? `MRR ${formatRevenue(kpis.mrr)}` : undefined}
        />
        <KPICard
          label="Active Academies"
          value={kpis?.active_academies ?? "—"}
        />
        <KPICard
          label="Total Athletes"
          value={kpis?.total_athletes?.toLocaleString() ?? "—"}
        />
        <KPICard
          label="Platform Utilization"
          value={kpis ? `${kpis.platform_utilization.toFixed(1)}%` : "—"}
          sub={
            kpis
              ? `${kpis.revenue_growth_pct >= 0 ? "+" : ""}${kpis.revenue_growth_pct.toFixed(1)}% growth`
              : undefined
          }
        />
      </div>

      {/* academy health leaderboard */}
      <Card title="Academy Health Leaderboard">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-xs uppercase tracking-wider text-[var(--text-muted)] border-b border-[var(--border-subtle)]">
                <th className="pb-3 text-left font-medium w-8">#</th>
                <th className="pb-3 text-left font-medium">Academy</th>
                <th className="pb-3 text-left font-medium">Sport</th>
                <th className="pb-3 text-left font-medium">Health</th>
                <th className="pb-3 text-right font-medium">Revenue</th>
                <th className="pb-3 text-right font-medium">Athletes</th>
                <th className="pb-3 text-right font-medium">Utilization</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[var(--border-subtle)]">
              {sorted.map((academy, index) => (
                <tr
                  key={academy.id}
                  className="hover:bg-[var(--bg-card)]/40 transition-colors"
                >
                  <td className="py-3 text-[var(--text-muted)] font-mono text-xs">
                    {index + 1}
                  </td>
                  <td className="py-3">
                    <p className="font-medium text-[var(--text-primary)]">
                      {academy.name}
                    </p>
                    <p className="text-xs text-[var(--text-muted)]">
                      {academy.region}
                    </p>
                  </td>
                  <td className="py-3 text-[var(--text-secondary)] capitalize">
                    {academy.sport_type}
                  </td>
                  <td className="py-3">
                    <div className="flex items-center gap-2">
                      <HealthScoreLabel score={academy.health_score} />
                      <HealthBar score={academy.health_score} />
                    </div>
                  </td>
                  <td className="py-3 text-right font-mono text-[var(--text-primary)]">
                    {formatRevenue(academy.monthly_revenue)}
                  </td>
                  <td className="py-3 text-right text-[var(--text-secondary)]">
                    {academy.active_athletes}
                  </td>
                  <td className="py-3 text-right text-[var(--text-secondary)]">
                    {academy.utilization_rate.toFixed(1)}%
                  </td>
                </tr>
              ))}
              {sorted.length === 0 && (
                <tr>
                  <td
                    colSpan={7}
                    className="py-8 text-center text-[var(--text-muted)]"
                  >
                    No academies found.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
}
