"use client";

import Link from "next/link";
import { PageLoader, PageHeader } from "@/components/ui/shared";
import { usePlatformAcademies } from "@/hooks/use-platform";
import type { AcademyMetrics } from "@/types";

function formatRevenue(n: number) {
  if (n >= 1000) return `$${(n / 1000).toFixed(1)}k`;
  return `$${n}`;
}

function sportEmoji(sport: string): string {
  const map: Record<string, string> = {
    soccer: "⚽",
    football: "⚽",
    tennis: "🎾",
    basketball: "🏀",
    swimming: "🏊",
    volleyball: "🏐",
  };
  const lower = sport.toLowerCase();
  for (const [key, emoji] of Object.entries(map)) {
    if (lower.includes(key)) return emoji;
  }
  return "🏟️";
}

function healthColor(score: number): string {
  if (score >= 80) return "var(--accent-emerald)";
  if (score >= 60) return "var(--accent-amber)";
  return "var(--accent-rose)";
}

function HealthBadge({ score }: { score: number }) {
  const color = healthColor(score);
  return (
    <span
      className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-xs font-semibold"
      style={{
        background: `${color}18`,
        color,
        border: `1px solid ${color}30`,
      }}
    >
      <span
        className="w-1.5 h-1.5 rounded-full"
        style={{ background: color }}
      />
      {score} health
    </span>
  );
}

function AcademyCard({ academy }: { academy: AcademyMetrics }) {
  return (
    <Link href={`/platform/academies/${academy.id}`}>
      <div className="card-glass rounded-xl p-5 hover:border-[var(--border-active)] transition-all duration-200 cursor-pointer h-full flex flex-col gap-4">
        {/* header */}
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-3">
            <span className="text-2xl">{sportEmoji(academy.sport_type)}</span>
            <div>
              <p className="font-display font-semibold text-[var(--text-primary)] leading-tight">
                {academy.name}
              </p>
              <p className="text-xs text-[var(--text-muted)] mt-0.5">
                {academy.region}
              </p>
            </div>
          </div>
          <HealthBadge score={academy.health_score} />
        </div>

        {/* stats */}
        <div className="grid grid-cols-3 gap-3 text-center">
          <div>
            <p
              className="font-mono font-semibold text-sm"
              style={{ color: "var(--accent-cyan)" }}
            >
              {formatRevenue(academy.monthly_revenue)}
            </p>
            <p className="text-xs text-[var(--text-muted)] mt-0.5">Revenue</p>
          </div>
          <div>
            <p className="font-mono font-semibold text-sm text-[var(--text-primary)]">
              {academy.active_athletes}
            </p>
            <p className="text-xs text-[var(--text-muted)] mt-0.5">Athletes</p>
          </div>
          <div>
            <p className="font-mono font-semibold text-sm text-[var(--text-primary)]">
              {academy.utilization_rate.toFixed(0)}%
            </p>
            <p className="text-xs text-[var(--text-muted)] mt-0.5">
              Utilization
            </p>
          </div>
        </div>

        {/* health bar */}
        <div>
          <div className="flex items-center justify-between mb-1">
            <span className="text-xs text-[var(--text-muted)]">
              Health Score
            </span>
          </div>
          <div className="h-1.5 rounded-full bg-[var(--bg-secondary)]">
            <div
              className="h-1.5 rounded-full transition-all"
              style={{
                width: `${academy.health_score}%`,
                background: healthColor(academy.health_score),
              }}
            />
          </div>
        </div>
      </div>
    </Link>
  );
}

export default function AcademiesPage() {
  const { data, isLoading } = usePlatformAcademies();

  if (isLoading) return <PageLoader />;

  const academies = (data as AcademyMetrics[] | undefined) || [];

  return (
    <div className="space-y-6">
      <PageHeader
        title="Academies"
        description={`${academies.length} academies on the platform`}
      />

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
        {academies.map((academy) => (
          <AcademyCard key={academy.id} academy={academy} />
        ))}
      </div>

      {academies.length === 0 && (
        <div className="flex flex-col items-center justify-center py-20 text-center">
          <p className="text-4xl mb-4">🏟️</p>
          <p className="font-display text-lg font-semibold mb-1">
            No academies yet
          </p>
          <p className="text-sm text-[var(--text-secondary)]">
            Academies will appear here once they are onboarded to the platform.
          </p>
        </div>
      )}
    </div>
  );
}
