"use client";

import { useFeatureFlags, useAuditLogs } from "@/hooks/use-data";
import { PageHeader, Card, PageLoader } from "@/components/ui/shared";
import { formatDate } from "@/lib/utils";
import { api } from "@/lib/api";
import { useQueryClient } from "@tanstack/react-query";
import { Shield, Flag, ScrollText, ToggleLeft, ToggleRight } from "lucide-react";
import type { FeatureFlag, AuditLog } from "@/types";

export default function SettingsPage() {
  const { data: flags, isLoading: flagsLoading } = useFeatureFlags();
  const { data: logs, isLoading: logsLoading } = useAuditLogs(1);
  const qc = useQueryClient();

  const handleToggle = async (flagId: string, currentState: boolean) => {
    try {
      await api.toggleFeatureFlag(flagId, !currentState);
      qc.invalidateQueries({ queryKey: ["feature-flags"] });
    } catch (e) {
      console.error("Toggle failed:", e);
    }
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <PageHeader
        title="Settings"
        description="Organization configuration, feature flags, and audit trail"
      />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* feature flags */}
        <Card
          title="Feature Flags"
          actions={
            <Flag className="w-4 h-4 text-[var(--text-muted)]" />
          }
        >
          {flagsLoading ? (
            <PageLoader />
          ) : (
            <div className="space-y-3">
              {((flags as FeatureFlag[]) ?? []).map((flag) => (
                <div
                  key={flag.id}
                  className="flex items-center justify-between p-3 rounded-lg bg-[var(--bg-secondary)]"
                >
                  <div>
                    <p className="text-sm font-medium capitalize">
                      {flag.feature_key.replace(/_/g, " ")}
                    </p>
                    <p className="text-xs text-[var(--text-muted)] font-mono mt-0.5">
                      {flag.feature_key}
                    </p>
                  </div>
                  <button
                    onClick={() => handleToggle(flag.id, flag.enabled)}
                    className="transition-colors"
                  >
                    {flag.enabled ? (
                      <ToggleRight className="w-8 h-8 text-accent-emerald" />
                    ) : (
                      <ToggleLeft className="w-8 h-8 text-[var(--text-muted)]" />
                    )}
                  </button>
                </div>
              ))}
            </div>
          )}
        </Card>

        {/* audit logs */}
        <Card
          title="Audit Trail"
          actions={
            <ScrollText className="w-4 h-4 text-[var(--text-muted)]" />
          }
        >
          {logsLoading ? (
            <PageLoader />
          ) : (
            <div className="space-y-2 max-h-[400px] overflow-y-auto">
              {((logs as AuditLog[]) ?? []).length === 0 ? (
                <p className="py-8 text-center text-sm text-[var(--text-muted)]">
                  No audit logs yet.
                </p>
              ) : (
                ((logs as AuditLog[]) ?? []).map((log) => (
                  <div
                    key={log.id}
                    className="p-3 rounded-lg bg-[var(--bg-secondary)] border-l-2 border-erebys-600"
                  >
                    <div className="flex items-center justify-between">
                      <p className="text-sm font-medium capitalize">
                        {log.action.replace(/_/g, " ")}
                      </p>
                      <span className="text-xs text-[var(--text-muted)] font-mono">
                        {formatDate(log.created_at)}
                      </span>
                    </div>
                    <p className="text-xs text-[var(--text-secondary)] mt-0.5">
                      {log.resource_type}
                      {log.resource_id && ` · ${log.resource_id.slice(0, 8)}…`}
                    </p>
                    {log.details && (
                      <pre className="mt-1.5 text-xs text-[var(--text-muted)] font-mono bg-[var(--bg-primary)] rounded p-2 overflow-x-auto">
                        {JSON.stringify(log.details, null, 2)}
                      </pre>
                    )}
                  </div>
                ))
              )}
            </div>
          )}
        </Card>
      </div>
    </div>
  );
}
