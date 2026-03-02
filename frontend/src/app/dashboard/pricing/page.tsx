"use client";

import { useState } from "react";
import {
  usePricingRecommendations,
  useWhatIfSimulate,
  useChangeRequests,
  useEvents,
  useGenerateRecommendation,
  useApproveChangeRequest,
  useCreateChangeRequest,
} from "@/hooks/use-data";
import { useToast } from "@/lib/toast-context";
import {
  PageHeader,
  Card,
  PageLoader,
  StatusBadge,
} from "@/components/ui/shared";
import { WhatIfChart } from "@/components/charts";
import { formatCurrency } from "@/lib/utils";
import {
  TrendingUp,
  TrendingDown,
  Zap,
  ArrowRight,
  Check,
  BarChart3,
  Sparkles,
} from "lucide-react";
import type { PricingRecommendation, Event, WhatIfResult } from "@/types";

export default function PricingPage() {
  const { data: recs, isLoading: recsLoading } = usePricingRecommendations();
  const { data: events } = useEvents();
  const { data: changeRequests } = useChangeRequests();
  const generateRec = useGenerateRecommendation();
  const approveRequest = useApproveChangeRequest();
  const whatIf = useWhatIfSimulate();
  const createChangeRequest = useCreateChangeRequest();
  const toast = useToast();

  const [selectedEvent, setSelectedEvent] = useState<string | null>(null);
  const [whatIfData, setWhatIfData] = useState<WhatIfResult[] | null>(null);

  const handleGenerate = (eventId: string) => {
    generateRec.mutate(eventId);
  };

  const handleWhatIf = (eventId: string, basePrice: number) => {
    const prices = [
      Math.round(basePrice * 0.7),
      Math.round(basePrice * 0.85),
      Math.round(basePrice),
      Math.round(basePrice * 1.15),
      Math.round(basePrice * 1.3),
      Math.round(basePrice * 1.5),
    ];
    setSelectedEvent(eventId);
    whatIf.mutate(
      { eventId, prices },
      {
        onSuccess: (data) => setWhatIfData(data),
      }
    );
  };

  if (recsLoading) return <PageLoader />;

  const recommendations = (recs as PricingRecommendation[]) ?? [];
  const eventMap = new Map((events as Event[])?.map((e) => [e.id, e]) ?? []);

  return (
    <div className="space-y-6 animate-fade-in">
      <PageHeader
        title="Dynamic Pricing Engine"
        description="ML-powered pricing recommendations with demand modeling"
        actions={
          <div className="flex gap-2">
            <button className="btn-secondary flex items-center gap-2">
              <BarChart3 className="w-4 h-4" />
              View All Change Requests
            </button>
          </div>
        }
      />

      {/* recommendations grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {recommendations.length === 0 ? (
          <Card className="lg:col-span-2">
            <div className="py-12 text-center">
              <Sparkles className="w-8 h-8 text-[var(--text-muted)] mx-auto mb-3" />
              <h3 className="font-display text-lg font-semibold mb-1">
                No Recommendations Yet
              </h3>
              <p className="text-sm text-[var(--text-secondary)] mb-4">
                Select an event below to generate a pricing recommendation.
              </p>

              <div className="max-w-md mx-auto space-y-2">
                {((events as Event[]) ?? []).slice(0, 5).map((evt) => (
                  <button
                    key={evt.id}
                    onClick={() => handleGenerate(evt.id)}
                    disabled={generateRec.isPending}
                    className="w-full btn-secondary flex items-center justify-between"
                  >
                    <span className="truncate">{evt.title}</span>
                    <Zap className="w-4 h-4 text-accent-amber shrink-0" />
                  </button>
                ))}
              </div>
            </div>
          </Card>
        ) : (
          recommendations.map((rec) => {
            const event = eventMap.get(rec.event_id);
            const isIncrease = rec.price_change_pct > 0;

            return (
              <div key={rec.id} className="card-glass rounded-xl p-5 space-y-4">
                {/* header */}
                <div className="flex items-start justify-between">
                  <div>
                    <p className="font-display font-semibold">
                      {event?.title ?? "Unknown Event"}
                    </p>
                    <p className="text-xs text-[var(--text-muted)] capitalize mt-0.5">
                      {event?.event_type}
                    </p>
                  </div>
                  <div className="flex items-center gap-2">
                    <div
                      className={`px-2 py-1 rounded-full text-xs font-mono font-medium ${
                        rec.confidence_score >= 70
                          ? "bg-emerald-500/10 text-accent-emerald"
                          : rec.confidence_score >= 40
                            ? "bg-amber-500/10 text-accent-amber"
                            : "bg-rose-500/10 text-accent-rose"
                      }`}
                    >
                      {rec.confidence_score}% conf
                    </div>
                  </div>
                </div>

                {/* price comparison */}
                <div className="flex items-center gap-4 p-4 rounded-lg bg-[var(--bg-secondary)]">
                  <div className="text-center">
                    <p className="text-xs text-[var(--text-muted)] mb-1">
                      Current
                    </p>
                    <p className="font-display text-xl font-bold">
                      {formatCurrency(rec.current_price)}
                    </p>
                  </div>

                  <ArrowRight className="w-5 h-5 text-[var(--text-muted)]" />

                  <div className="text-center">
                    <p className="text-xs text-[var(--text-muted)] mb-1">
                      Suggested
                    </p>
                    <p
                      className={`font-display text-xl font-bold ${
                        isIncrease ? "text-accent-emerald" : "text-accent-amber"
                      }`}
                    >
                      {formatCurrency(rec.suggested_price)}
                    </p>
                  </div>

                  <div className="ml-auto text-right">
                    <div
                      className={`inline-flex items-center gap-1 text-sm font-mono font-medium ${
                        isIncrease ? "text-accent-emerald" : "text-accent-rose"
                      }`}
                    >
                      {isIncrease ? (
                        <TrendingUp className="w-4 h-4" />
                      ) : (
                        <TrendingDown className="w-4 h-4" />
                      )}
                      {isIncrease ? "+" : ""}
                      {rec.price_change_pct.toFixed(1)}%
                    </div>
                    <p className="text-xs text-[var(--text-muted)] mt-0.5">
                      Rev impact:{" "}
                      {rec.expected_revenue_change >= 0 ? "+" : ""}
                      {rec.expected_revenue_change.toFixed(1)}%
                    </p>
                  </div>
                </div>

                {/* explanation */}
                <p className="text-sm text-[var(--text-secondary)] leading-relaxed">
                  {rec.explanation}
                </p>

                {/* drivers */}
                {rec.drivers && typeof rec.drivers === "object" && !Array.isArray(rec.drivers) && (
                  <div className="space-y-1.5">
                    <p className="text-xs font-medium text-[var(--text-muted)] uppercase tracking-wider">
                      Key Drivers
                    </p>
                    {Object.entries(rec.drivers)
                      .filter(([key]) => key !== "factors")
                      .slice(0, 4)
                      .map(([name, info]) => {
                        const driverInfo = info as { impact: string; value: string };
                        return (
                          <div key={name} className="flex items-center justify-between text-xs">
                            <span className="text-[var(--text-secondary)]">{name}</span>
                            <span
                              className={`font-mono ${
                                driverInfo.impact === "upward"
                                  ? "text-accent-emerald"
                                  : "text-accent-rose"
                              }`}
                            >
                              {driverInfo.impact === "upward" ? "↑" : "↓"} {driverInfo.value}
                            </span>
                          </div>
                        );
                      })}
                  </div>
                )}

                {/* actions */}
                <div className="flex gap-2 pt-2">
                  <button
                    onClick={() =>
                      handleWhatIf(rec.event_id, rec.current_price)
                    }
                    className="btn-secondary flex-1 flex items-center justify-center gap-2 text-xs"
                  >
                    <BarChart3 className="w-3.5 h-3.5" />
                    What-If
                  </button>
                  <button
                    onClick={() => {
                      createChangeRequest.mutate(
                        {
                          event_id: rec.event_id,
                          new_price: rec.suggested_price,
                          recommendation_id: rec.id,
                          reason: `ML recommendation: ${rec.explanation?.slice(0, 100) ?? ""}`,
                        },
                        {
                          onSuccess: () => toast.success("Price change request submitted for approval"),
                          onError: () => toast.error("Failed to submit price change request"),
                        }
                      );
                    }}
                    disabled={createChangeRequest.isPending}
                    className="btn-primary flex-1 flex items-center justify-center gap-2 text-xs"
                  >
                    <Check className="w-3.5 h-3.5" />
                    Apply Price
                  </button>
                </div>
              </div>
            );
          })
        )}
      </div>

      {/* what-if simulator */}
      {whatIfData && (
        <Card
          title="What-If Price Simulator"
          actions={
            <button
              onClick={() => setWhatIfData(null)}
              className="text-xs text-[var(--text-muted)] hover:text-[var(--text-primary)]"
            >
              Close
            </button>
          }
        >
          <WhatIfChart
            data={whatIfData}
            currentPrice={
              eventMap.get(selectedEvent ?? "")?.current_price ?? 100
            }
          />
        </Card>
      )}

      {/* pending change requests */}
      {changeRequests && (changeRequests as unknown[]).length > 0 && (
        <Card title="Pending Price Change Requests">
          <div className="space-y-3">
            {(
              changeRequests as Array<{
                id: string;
                event_id: string;
                old_price: number;
                new_price: number;
                status: string;
                reason?: string;
              }>
            ).map((req) => (
              <div
                key={req.id}
                className="flex items-center justify-between p-3 rounded-lg bg-[var(--bg-secondary)]"
              >
                <div>
                  <p className="text-sm font-medium">
                    {eventMap.get(req.event_id)?.title ?? req.event_id}
                  </p>
                  <p className="text-xs text-[var(--text-muted)] mt-0.5">
                    {formatCurrency(req.old_price)} → {formatCurrency(req.new_price)}
                    {req.reason && ` · ${req.reason}`}
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  <StatusBadge status={req.status} />
                  {req.status === "pending" && (
                    <button
                      onClick={() => approveRequest.mutate(req.id)}
                      className="btn-primary text-xs px-3 py-1.5"
                    >
                      Approve
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}
    </div>
  );
}
