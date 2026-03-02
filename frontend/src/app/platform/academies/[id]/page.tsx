"use client";

import { useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { ChevronLeft } from "lucide-react";
import { PageLoader, Card, PageHeader } from "@/components/ui/shared";
import { usePlatformAcademy } from "@/hooks/use-platform";
import type { AcademyMetrics } from "@/types";

function formatRevenue(n: number) {
  if (n >= 1000) return `$${(n / 1000).toFixed(1)}k`;
  return `$${n}`;
}

function healthColor(score: number): string {
  if (score >= 80) return "var(--accent-emerald)";
  if (score >= 60) return "var(--accent-amber)";
  return "var(--accent-rose)";
}

function StatRow({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="flex items-center justify-between py-3 border-b border-[var(--border-subtle)] last:border-0">
      <span className="text-sm text-[var(--text-secondary)]">{label}</span>
      <span className="text-sm font-medium text-[var(--text-primary)]">
        {value}
      </span>
    </div>
  );
}

const TABS = ["Overview", "Events", "Users"] as const;
type Tab = (typeof TABS)[number];

export default function AcademyDetailPage() {
  const { id } = useParams<{ id: string }>();
  const { data, isLoading } = usePlatformAcademy(id);
  const [activeTab, setActiveTab] = useState<Tab>("Overview");

  if (isLoading) return <PageLoader />;

  const academy = data as AcademyMetrics | undefined;

  if (!academy) {
    return (
      <div className="py-20 text-center">
        <p className="text-[var(--text-muted)]">Academy not found.</p>
        <Link
          href="/platform/academies"
          className="mt-4 inline-flex items-center gap-1.5 text-sm"
          style={{ color: "var(--accent-cyan)" }}
        >
          <ChevronLeft className="w-4 h-4" /> Back to academies
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* back link */}
      <Link
        href="/platform/academies"
        className="inline-flex items-center gap-1.5 text-sm text-[var(--text-muted)] hover:text-[var(--text-primary)] transition-colors"
      >
        <ChevronLeft className="w-4 h-4" /> Back to Academies
      </Link>

      <PageHeader
        title={academy.name}
        description={`${academy.sport_type} · ${academy.region}`}
      />

      {/* tabs */}
      <div className="flex gap-1 border-b border-[var(--border-subtle)]">
        {TABS.map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-4 py-2.5 text-sm font-medium transition-colors border-b-2 -mb-px ${
              activeTab === tab
                ? "border-[var(--accent-cyan)] text-[var(--accent-cyan)]"
                : "border-transparent text-[var(--text-secondary)] hover:text-[var(--text-primary)]"
            }`}
          >
            {tab}
          </button>
        ))}
      </div>

      {/* overview tab */}
      {activeTab === "Overview" && (
        <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
          {/* key metrics */}
          <Card title="Key Metrics">
            <StatRow
              label="Monthly Revenue"
              value={formatRevenue(academy.monthly_revenue)}
            />
            <StatRow label="Active Athletes" value={academy.active_athletes} />
            <StatRow label="Events (month)" value={academy.events_count} />
            <StatRow
              label="Utilization Rate"
              value={`${academy.utilization_rate.toFixed(1)}%`}
            />
            <StatRow
              label="Athlete Retention"
              value={`${academy.athlete_retention_rate.toFixed(1)}%`}
            />
          </Card>

          {/* health */}
          <Card title="Health Score">
            <div className="flex flex-col items-center py-4 gap-4">
              <div
                className="text-5xl font-display font-bold"
                style={{ color: healthColor(academy.health_score) }}
              >
                {academy.health_score}
              </div>
              <div className="w-full h-2.5 rounded-full bg-[var(--bg-secondary)]">
                <div
                  className="h-2.5 rounded-full transition-all"
                  style={{
                    width: `${academy.health_score}%`,
                    background: healthColor(academy.health_score),
                  }}
                />
              </div>
              <p className="text-xs text-[var(--text-muted)]">
                {academy.health_score >= 80
                  ? "Excellent health — top performer"
                  : academy.health_score >= 60
                  ? "Good health — monitor trends"
                  : "Needs attention — review metrics"}
              </p>
            </div>
          </Card>

          {/* details */}
          <Card title="Academy Details" className="md:col-span-2">
            <StatRow label="Academy ID" value={academy.id} />
            <StatRow label="Sport Type" value={academy.sport_type} />
            <StatRow label="Region" value={academy.region} />
            <StatRow
              label="Created"
              value={new Date(academy.created_at).toLocaleDateString()}
            />
          </Card>
        </div>
      )}

      {/* events tab */}
      {activeTab === "Events" && (
        <Card title="Events">
          <div className="py-10 text-center text-[var(--text-muted)]">
            Event listing for this academy coming soon.
          </div>
        </Card>
      )}

      {/* users tab */}
      {activeTab === "Users" && (
        <Card title="Users">
          <div className="py-10 text-center text-[var(--text-muted)]">
            User listing for this academy coming soon.
          </div>
        </Card>
      )}
    </div>
  );
}
