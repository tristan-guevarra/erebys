"use client";

import { useInsights, useGenerateInsight } from "@/hooks/use-data";
import {
  PageHeader,
  Card,
  PageLoader,
  EmptyState,
} from "@/components/ui/shared";
import { formatDate } from "@/lib/utils";
import { Lightbulb, RefreshCw, FileText } from "lucide-react";
import type { InsightReport } from "@/types";

export default function InsightsPage() {
  const { data: insights, isLoading } = useInsights();
  const generate = useGenerateInsight();

  if (isLoading) return <PageLoader />;

  const reports = (insights as InsightReport[]) ?? [];

  return (
    <div className="space-y-6 animate-fade-in">
      <PageHeader
        title="Weekly Insights"
        description="AI-generated intelligence reports for your academy"
        actions={
          <button
            onClick={() => generate.mutate()}
            disabled={generate.isPending}
            className="btn-primary flex items-center gap-2"
          >
            <RefreshCw
              className={`w-4 h-4 ${generate.isPending ? "animate-spin" : ""}`}
            />
            Generate Report
          </button>
        }
      />

      {reports.length === 0 ? (
        <Card>
          <EmptyState
            icon={<Lightbulb className="w-10 h-10" />}
            title="No Reports Yet"
            description='Click "Generate Report" to create your first AI-powered weekly intelligence summary.'
          />
        </Card>
      ) : (
        <div className="space-y-4">
          {reports.map((report) => (
            <Card key={report.id} className="overflow-hidden">
              <div className="flex items-center gap-3 px-5 py-4 border-b border-[var(--border-subtle)] bg-[var(--bg-secondary)]/30">
                <FileText className="w-4 h-4 text-erebys-400" />
                <div>
                  <p className="font-display text-sm font-semibold capitalize">
                    {report.report_type} Report
                  </p>
                  <p className="text-xs text-[var(--text-muted)]">
                    {formatDate(report.period_start)} –{" "}
                    {formatDate(report.period_end)}
                  </p>
                </div>
              </div>

              <div className="p-5">
                {/* narrative (markdown-like rendering) */}
                <div className="prose-erebys text-sm text-[var(--text-secondary)] leading-relaxed whitespace-pre-wrap">
                  {report.narrative
                    .replace(/## /g, "")
                    .replace(/### /g, "")
                    .replace(/\*\*/g, "")}
                </div>

                {/* highlights */}
                {report.highlights && (
                  <div className="mt-4 grid grid-cols-2 md:grid-cols-5 gap-3">
                    {Object.entries(report.highlights).map(([key, val]) => (
                      <div
                        key={key}
                        className="p-2.5 rounded-lg bg-[var(--bg-secondary)] text-center"
                      >
                        <p className="text-xs text-[var(--text-muted)] capitalize mb-0.5">
                          {key.replace(/_/g, " ")}
                        </p>
                        <p className="font-mono text-sm font-medium">
                          {typeof val === "number"
                            ? key.includes("revenue")
                              ? `$${(val as number).toLocaleString()}`
                              : key.includes("rate") || key.includes("utilization")
                                ? `${val}%`
                                : val.toLocaleString()
                            : String(val)}
                        </p>
                      </div>
                    ))}
                  </div>
                )}

                {/* alerts */}
                {report.alerts &&
                  (report.alerts as { items?: Array<{ type: string; message: string }> })
                    .items && (
                    <div className="mt-4 space-y-2">
                      {(
                        (report.alerts as { items: Array<{ type: string; message: string }> })
                          .items
                      ).map((alert, i) => (
                        <div
                          key={i}
                          className="flex items-start gap-2 p-2.5 rounded-lg bg-amber-500/5 border border-amber-500/10 text-sm"
                        >
                          <span className="text-accent-amber">⚠️</span>
                          <span className="text-[var(--text-secondary)]">
                            {alert.message}
                          </span>
                        </div>
                      ))}
                    </div>
                  )}
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
