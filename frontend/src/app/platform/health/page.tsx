"use client";

import { PageLoader, PageHeader, Card } from "@/components/ui/shared";
import { usePlatformHealth } from "@/hooks/use-platform";
import type { SystemHealth } from "@/types";

function StatusDot({ status }: { status: string }) {
  const isOk = status === "ok" || status === "healthy";
  return (
    <span
      className="inline-flex items-center gap-1.5"
    >
      <span
        className="w-2 h-2 rounded-full"
        style={{ background: isOk ? "var(--accent-emerald)" : "var(--accent-rose)" }}
      />
      <span
        className="text-sm font-medium capitalize"
        style={{ color: isOk ? "var(--accent-emerald)" : "var(--accent-rose)" }}
      >
        {status}
      </span>
    </span>
  );
}

interface StatusCardProps {
  label: string;
  status: string;
  sub?: string;
}

function StatusCard({ label, sub, status }: StatusCardProps) {
  const isOk = status === "ok" || status === "healthy";
  return (
    <div
      className="card-glass rounded-xl p-5 border"
      style={{
        borderColor: isOk
          ? "rgba(16,185,129,0.2)"
          : "rgba(244,63,94,0.2)",
      }}
    >
      <p className="text-xs uppercase tracking-wider text-[var(--text-muted)] mb-3 font-medium">
        {label}
      </p>
      <StatusDot status={status} />
      {sub && (
        <p className="text-xs text-[var(--text-muted)] mt-2">{sub}</p>
      )}
    </div>
  );
}

function formatDateTime(val: string | null): string {
  if (!val) return "Never";
  return new Date(val).toLocaleString();
}

export default function HealthPage() {
  const { data, isLoading } = usePlatformHealth();

  if (isLoading) return <PageLoader />;

  const health = data as SystemHealth | undefined;

  return (
    <div className="space-y-6">
      <PageHeader
        title="System Health"
        description="Live infrastructure status — auto-refreshes every 30 seconds."
      />

      {/* status cards */}
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <StatusCard
          label="Database"
          status={health?.db_status ?? "unknown"}
          sub={health ? `Pool size: ${health.db_pool_size}` : undefined}
        />
        <StatusCard
          label="Redis"
          status={health?.redis_status ?? "unknown"}
        />
        <StatusCard
          label="Celery Workers"
          status={health?.celery_status ?? "unknown"}
        />
        <StatusCard
          label="Uptime"
          status={health?.uptime_status ?? "unknown"}
          sub={health ? `API v${health.api_version}` : undefined}
        />
      </div>

      {/* detail card */}
      <Card title="System Details">
        <div className="divide-y divide-[var(--border-subtle)]">
          <div className="flex items-center justify-between py-3">
            <span className="text-sm text-[var(--text-secondary)]">
              API Version
            </span>
            <span className="text-sm font-mono text-[var(--text-primary)]">
              {health?.api_version ?? "—"}
            </span>
          </div>
          <div className="flex items-center justify-between py-3">
            <span className="text-sm text-[var(--text-secondary)]">
              DB Pool Size
            </span>
            <span className="text-sm font-mono text-[var(--text-primary)]">
              {health?.db_pool_size ?? "—"}
            </span>
          </div>
          <div className="flex items-center justify-between py-3">
            <span className="text-sm text-[var(--text-secondary)]">
              Last Metrics Run
            </span>
            <span className="text-sm text-[var(--text-primary)]">
              {health ? formatDateTime(health.last_metrics_run) : "—"}
            </span>
          </div>
          <div className="flex items-center justify-between py-3">
            <span className="text-sm text-[var(--text-secondary)]">
              Last Insight Run
            </span>
            <span className="text-sm text-[var(--text-primary)]">
              {health ? formatDateTime(health.last_insight_run) : "—"}
            </span>
          </div>
        </div>
      </Card>
    </div>
  );
}
