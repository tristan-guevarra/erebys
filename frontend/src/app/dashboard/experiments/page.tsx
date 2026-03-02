"use client";

import { useState } from "react";
import { useExperiments, useCreateExperiment, useEvents } from "@/hooks/use-data";
import { PageHeader, Card, PageLoader, StatusBadge, EmptyState } from "@/components/ui/shared";
import { formatCurrency } from "@/lib/utils";
import { FlaskConical, Plus, TrendingUp, X } from "lucide-react";
import { useToast } from "@/lib/toast-context";
import type { Experiment, Event } from "@/types";

function NewExperimentModal({ onClose }: { onClose: () => void }) {
  const [form, setForm] = useState({
    name: "",
    description: "",
    event_id: "",
    variant_a_price: 100,
    variant_b_price: 120,
    traffic_split: 0.5,
  });
  const [errors, setErrors] = useState<Record<string, string>>({});
  const createExperiment = useCreateExperiment();
  const { data: events } = useEvents();
  const toast = useToast();

  const set = (key: string, value: string | number) =>
    setForm((f) => ({ ...f, [key]: value }));

  const validate = () => {
    const errs: Record<string, string> = {};
    if (!form.name.trim()) errs.name = "Name is required";
    if (form.variant_a_price <= 0) errs.variant_a_price = "Must be > 0";
    if (form.variant_b_price <= 0) errs.variant_b_price = "Must be > 0";
    if (form.variant_a_price === form.variant_b_price)
      errs.variant_b_price = "Variant B must differ from Variant A";
    return errs;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const errs = validate();
    if (Object.keys(errs).length > 0) {
      setErrors(errs);
      return;
    }
    try {
      await createExperiment.mutateAsync({
        ...form,
        event_id: form.event_id || null,
      });
      toast.success("Experiment created successfully");
      onClose();
    } catch {
      toast.error("Failed to create experiment. Please try again.");
    }
  };

  const eventList = (events as Event[]) ?? [];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
      <div className="w-full max-w-md bg-[var(--bg-card)] rounded-2xl border border-[var(--border-subtle)] shadow-2xl">
        <div className="flex items-center justify-between px-6 py-4 border-b border-[var(--border-subtle)]">
          <h2 className="font-display text-lg font-semibold">New Experiment</h2>
          <button onClick={onClose} className="p-1.5 rounded-lg hover:bg-[var(--bg-secondary)] text-[var(--text-muted)]">
            <X className="w-4 h-4" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          <div>
            <label className="block text-xs font-medium text-[var(--text-secondary)] mb-1">Experiment Name *</label>
            <input
              className="input w-full"
              value={form.name}
              onChange={(e) => set("name", e.target.value)}
              placeholder="Summer Camp Price Test"
            />
            {errors.name && <p className="text-xs text-accent-rose mt-1">{errors.name}</p>}
          </div>

          <div>
            <label className="block text-xs font-medium text-[var(--text-secondary)] mb-1">Description</label>
            <input
              className="input w-full"
              value={form.description}
              onChange={(e) => set("description", e.target.value)}
              placeholder="Testing a 20% price increase..."
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-[var(--text-secondary)] mb-1">Event (optional)</label>
            <select className="input w-full" value={form.event_id} onChange={(e) => set("event_id", e.target.value)}>
              <option value="">— All events (org-wide) —</option>
              {eventList.map((evt) => (
                <option key={evt.id} value={evt.id}>{evt.title}</option>
              ))}
            </select>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-medium text-[var(--text-secondary)] mb-1">Variant A — Control ($)</label>
              <input
                type="number"
                min="1"
                step="5"
                className="input w-full"
                value={form.variant_a_price}
                onChange={(e) => set("variant_a_price", parseFloat(e.target.value) || 0)}
              />
              {errors.variant_a_price && <p className="text-xs text-accent-rose mt-1">{errors.variant_a_price}</p>}
            </div>
            <div>
              <label className="block text-xs font-medium text-[var(--text-secondary)] mb-1">Variant B — Test ($)</label>
              <input
                type="number"
                min="1"
                step="5"
                className="input w-full"
                value={form.variant_b_price}
                onChange={(e) => set("variant_b_price", parseFloat(e.target.value) || 0)}
              />
              {errors.variant_b_price && <p className="text-xs text-accent-rose mt-1">{errors.variant_b_price}</p>}
            </div>
          </div>

          <div>
            <label className="block text-xs font-medium text-[var(--text-secondary)] mb-1">
              Traffic Split — {((1 - form.traffic_split) * 100).toFixed(0)}% A / {(form.traffic_split * 100).toFixed(0)}% B
            </label>
            <input
              type="range"
              min="0.1"
              max="0.9"
              step="0.1"
              className="w-full accent-erebys-500"
              value={form.traffic_split}
              onChange={(e) => set("traffic_split", parseFloat(e.target.value))}
            />
          </div>

          <div className="flex gap-3 pt-2">
            <button type="button" onClick={onClose} className="btn-secondary flex-1">Cancel</button>
            <button
              type="submit"
              disabled={createExperiment.isPending}
              className="btn-primary flex-1"
            >
              {createExperiment.isPending ? "Creating…" : "Create Experiment"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default function ExperimentsPage() {
  const { data: experiments, isLoading } = useExperiments();
  const [showNew, setShowNew] = useState(false);

  if (isLoading) return <PageLoader />;

  const exps = (experiments as Experiment[]) ?? [];

  return (
    <>
      {showNew && <NewExperimentModal onClose={() => setShowNew(false)} />}

      <div className="space-y-6 animate-fade-in">
        <PageHeader
          title="Pricing Experiments"
          description="A/B tests to validate pricing strategies"
          actions={
            <button onClick={() => setShowNew(true)} className="btn-primary flex items-center gap-2">
              <Plus className="w-4 h-4" />
              New Experiment
            </button>
          }
        />

        {exps.length === 0 ? (
          <Card>
            <EmptyState
              icon={<FlaskConical className="w-10 h-10" />}
              title="No Experiments Yet"
              description="Create an A/B test to validate pricing changes before rolling them out to all athletes."
            />
          </Card>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {exps.map((exp) => (
              <div key={exp.id} className="card-glass rounded-xl p-5 space-y-4">
                <div className="flex items-start justify-between">
                  <div>
                    <h3 className="font-display font-semibold">{exp.name}</h3>
                    {exp.description && (
                      <p className="text-xs text-[var(--text-muted)] mt-0.5">{exp.description}</p>
                    )}
                  </div>
                  <StatusBadge status={exp.status} />
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div className="p-3 rounded-lg bg-[var(--bg-secondary)] text-center">
                    <p className="text-xs text-[var(--text-muted)] mb-1">Variant A (Control)</p>
                    <p className="font-display text-lg font-bold">{formatCurrency(exp.variant_a_price)}</p>
                  </div>
                  <div className="p-3 rounded-lg bg-erebys-800/50 border border-erebys-600/20 text-center">
                    <p className="text-xs text-erebys-400 mb-1">Variant B (Test)</p>
                    <p className="font-display text-lg font-bold text-erebys-300">{formatCurrency(exp.variant_b_price)}</p>
                  </div>
                </div>

                <div className="flex items-center justify-between text-xs text-[var(--text-muted)]">
                  <span>
                    Traffic: {((1 - exp.traffic_split) * 100).toFixed(0)}% / {(exp.traffic_split * 100).toFixed(0)}%
                  </span>
                  {exp.start_date && <span>Started: {exp.start_date}</span>}
                </div>

                {exp.results && (
                  <div className="p-3 rounded-lg bg-emerald-500/5 border border-emerald-500/10">
                    <div className="flex items-center gap-2 mb-2">
                      <TrendingUp className="w-4 h-4 text-accent-emerald" />
                      <span className="text-sm font-medium">Results</span>
                    </div>
                    <div className="grid grid-cols-2 gap-3 text-xs">
                      <div>
                        <p className="text-[var(--text-muted)]">Variant A</p>
                        <p>
                          {exp.results.variant_a.bookings} bookings ·{" "}
                          {(exp.results.variant_a.conversion_rate * 100).toFixed(1)}% CVR
                        </p>
                      </div>
                      <div>
                        <p className="text-[var(--text-muted)]">Variant B</p>
                        <p>
                          {exp.results.variant_b.bookings} bookings ·{" "}
                          {(exp.results.variant_b.conversion_rate * 100).toFixed(1)}% CVR
                        </p>
                      </div>
                    </div>
                    {exp.results.winner && (
                      <p className="mt-2 text-xs font-medium text-accent-emerald">
                        Winner: Variant {exp.results.winner}
                        {exp.results.lift_pct != null && ` (+${exp.results.lift_pct.toFixed(1)}% lift)`}
                      </p>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </>
  );
}
