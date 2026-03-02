"use client";

import {
  useLTVDistribution,
  useCohorts,
  useNoShowRisks,
} from "@/hooks/use-data";
import { PageHeader, Card, PageLoader, StatusBadge } from "@/components/ui/shared";
import { LTVChart, CohortChart } from "@/components/charts";
import { formatCurrency } from "@/lib/utils";
import { Users, Shield, AlertTriangle } from "lucide-react";
import type { NoShowRisk, AthleteLTVBucket, CohortRow } from "@/types";

export default function AthletesPage() {
  const { data: ltv, isLoading: ltvLoading } = useLTVDistribution();
  const { data: cohorts, isLoading: cohortsLoading } = useCohorts(6);
  const { data: risks, isLoading: risksLoading } = useNoShowRisks(15);

  if (ltvLoading && cohortsLoading) return <PageLoader />;

  return (
    <div className="space-y-6 animate-fade-in">
      <PageHeader
        title="Athlete Intelligence"
        description="Lifetime value, retention cohorts, and risk analysis"
      />

      {/* ltv distribution */}
      <Card title="Lifetime Value Distribution" actions={
        <span className="text-xs text-[var(--text-muted)]">
          {(ltv as AthleteLTVBucket[])?.reduce((s, b) => s + b.count, 0) ?? 0} athletes
        </span>
      }>
        {ltvLoading ? (
          <PageLoader />
        ) : (
          <>
            <LTVChart data={(ltv as AthleteLTVBucket[]) ?? []} />
            <div className="mt-4 grid grid-cols-2 md:grid-cols-5 gap-3">
              {((ltv as AthleteLTVBucket[]) ?? []).map((bucket) => (
                <div
                  key={bucket.bucket}
                  className="p-3 rounded-lg bg-[var(--bg-secondary)] text-center"
                >
                  <p className="text-xs text-[var(--text-muted)] mb-1">
                    {bucket.bucket}
                  </p>
                  <p className="font-display text-lg font-bold">
                    {bucket.count}
                  </p>
                  <p className="text-xs text-[var(--text-secondary)]">
                    avg {formatCurrency(bucket.avg_ltv)}
                  </p>
                </div>
              ))}
            </div>
          </>
        )}
      </Card>

      {/* cohort retention */}
      <Card title="Monthly Cohort Retention">
        {cohortsLoading ? (
          <PageLoader />
        ) : (cohorts as CohortRow[])?.length ? (
          <CohortChart data={(cohorts as CohortRow[]) ?? []} />
        ) : (
          <div className="py-8 text-center text-[var(--text-muted)] text-sm">
            Not enough data for cohort analysis yet.
          </div>
        )}
      </Card>

      {/* no-show risk table */}
      <Card
        title="No-Show Risk Analysis"
        actions={
          <div className="flex items-center gap-2 text-xs">
            <div className="flex items-center gap-1">
              <span className="w-2 h-2 rounded-full bg-accent-emerald" />
              Low
            </div>
            <div className="flex items-center gap-1">
              <span className="w-2 h-2 rounded-full bg-accent-amber" />
              Medium
            </div>
            <div className="flex items-center gap-1">
              <span className="w-2 h-2 rounded-full bg-accent-rose" />
              High
            </div>
          </div>
        }
      >
        {risksLoading ? (
          <PageLoader />
        ) : (
          <div className="space-y-2">
            {((risks as NoShowRisk[]) ?? []).map((risk) => (
              <div
                key={risk.athlete_id}
                className="flex items-center justify-between p-3 rounded-lg bg-[var(--bg-secondary)] hover:bg-[var(--bg-card-hover)] transition-colors"
              >
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-full bg-erebys-700 flex items-center justify-center text-xs font-bold text-erebys-300">
                    {risk.athlete_name
                      .split(" ")
                      .map((n) => n[0])
                      .join("")}
                  </div>
                  <div>
                    <p className="text-sm font-medium">{risk.athlete_name}</p>
                    <p className="text-xs text-[var(--text-muted)]">
                      {risk.total_bookings} bookings · {risk.no_show_rate.toFixed(0)}% no-show rate
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-3">
                  <div className="text-right">
                    <p className="text-xs text-[var(--text-muted)]">Risk Score</p>
                    <p className="font-mono text-sm font-medium">
                      {(risk.risk_score * 100).toFixed(0)}%
                    </p>
                  </div>
                  <StatusBadge status={risk.risk_level} />
                </div>
              </div>
            ))}
          </div>
        )}
      </Card>
    </div>
  );
}
