"use client";

import { Settings, Flag, CreditCard, Bell, Shield } from "lucide-react";
import { PageHeader, Card } from "@/components/ui/shared";

const UPCOMING_FEATURES = [
  {
    icon: Flag,
    label: "Feature Flag Management",
    description:
      "Toggle platform-wide feature flags and per-academy overrides without a deployment.",
  },
  {
    icon: CreditCard,
    label: "Billing & Subscription Config",
    description:
      "Manage academy billing plans, pricing tiers, trial periods, and invoice settings.",
  },
  {
    icon: Bell,
    label: "Alert & Notification Rules",
    description:
      "Configure automated alerts for health score drops, revenue anomalies, and utilization thresholds.",
  },
  {
    icon: Shield,
    label: "Security & Access Policy",
    description:
      "Set platform-wide password policies, session timeouts, IP allowlists, and SSO configuration.",
  },
];

export default function PlatformSettingsPage() {
  return (
    <div className="space-y-6">
      <PageHeader
        title="Platform Settings"
        description="Global configuration for the Erebys Intelligence Suite."
      />

      <Card>
        <div className="flex flex-col items-center py-8 text-center gap-4">
          <div
            className="w-14 h-14 rounded-2xl flex items-center justify-center"
            style={{ background: "rgba(6,182,212,0.12)" }}
          >
            <Settings
              className="w-7 h-7"
              style={{ color: "var(--accent-cyan)" }}
            />
          </div>
          <div>
            <h2 className="font-display text-xl font-semibold mb-1">
              Platform configuration coming soon
            </h2>
            <p className="text-sm text-[var(--text-secondary)] max-w-md mx-auto">
              Superadmin settings for the entire Erebys platform are actively
              being built. The sections below outline what will be available
              here.
            </p>
          </div>
        </div>
      </Card>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        {UPCOMING_FEATURES.map((feature) => (
          <div
            key={feature.label}
            className="card-glass rounded-xl p-5 flex gap-4 opacity-60"
          >
            <div
              className="w-9 h-9 rounded-lg flex items-center justify-center shrink-0"
              style={{ background: "rgba(6,182,212,0.10)" }}
            >
              <feature.icon
                className="w-4.5 h-4.5"
                style={{ color: "var(--accent-cyan)" }}
              />
            </div>
            <div>
              <p className="text-sm font-semibold text-[var(--text-primary)] mb-0.5">
                {feature.label}
              </p>
              <p className="text-xs text-[var(--text-secondary)] leading-relaxed">
                {feature.description}
              </p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
