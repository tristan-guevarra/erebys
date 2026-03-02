"use client";

import { useState } from "react";
import { useEvents, useCreateEvent } from "@/hooks/use-data";
import { DataTable } from "@/components/ui/data-table";
import { PageHeader, PageLoader, StatusBadge } from "@/components/ui/shared";
import { formatCurrency, formatDate } from "@/lib/utils";
import { Download, Upload, Plus, X } from "lucide-react";
import { api } from "@/lib/api";
import { useToast } from "@/lib/toast-context";
import type { Event } from "@/types";

// new event form
interface NewEventForm {
  title: string;
  event_type: "camp" | "clinic" | "private";
  start_date: string;
  end_date: string;
  start_time: string;
  end_time: string;
  capacity: number;
  base_price: number;
  skill_level: string;
  location: string;
}

const EMPTY_FORM: NewEventForm = {
  title: "",
  event_type: "camp",
  start_date: "",
  end_date: "",
  start_time: "09:00",
  end_time: "12:00",
  capacity: 20,
  base_price: 100,
  skill_level: "intermediate",
  location: "",
};

function NewEventModal({ onClose }: { onClose: () => void }) {
  const [form, setForm] = useState<NewEventForm>(EMPTY_FORM);
  const [errors, setErrors] = useState<Partial<Record<keyof NewEventForm, string>>>({});
  const createEvent = useCreateEvent();
  const toast = useToast();

  const set = (key: keyof NewEventForm, value: string | number) =>
    setForm((f) => ({ ...f, [key]: value }));

  const validate = () => {
    const errs: Partial<Record<keyof NewEventForm, string>> = {};
    if (!form.title.trim()) errs.title = "Title is required";
    if (!form.start_date) errs.start_date = "Start date is required";
    if (!form.start_time) errs.start_time = "Start time is required";
    if (!form.end_time) errs.end_time = "End time is required";
    if (form.capacity < 1) errs.capacity = "Capacity must be at least 1";
    if (form.base_price < 0) errs.base_price = "Price must be positive";
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
      await createEvent.mutateAsync({
        ...form,
        current_price: form.base_price,
        status: "published",
      });
      toast.success("Event created successfully");
      onClose();
    } catch {
      toast.error("Failed to create event. Please try again.");
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
      <div className="w-full max-w-lg bg-[var(--bg-card)] rounded-2xl border border-[var(--border-subtle)] shadow-2xl">
        <div className="flex items-center justify-between px-6 py-4 border-b border-[var(--border-subtle)]">
          <h2 className="font-display text-lg font-semibold">New Event</h2>
          <button onClick={onClose} className="p-1.5 rounded-lg hover:bg-[var(--bg-secondary)] text-[var(--text-muted)]">
            <X className="w-4 h-4" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          <div>
            <label className="block text-xs font-medium text-[var(--text-secondary)] mb-1">Title *</label>
            <input
              className="input w-full"
              value={form.title}
              onChange={(e) => set("title", e.target.value)}
              placeholder="Summer Skills Camp"
            />
            {errors.title && <p className="text-xs text-accent-rose mt-1">{errors.title}</p>}
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-medium text-[var(--text-secondary)] mb-1">Type</label>
              <select className="input w-full" value={form.event_type} onChange={(e) => set("event_type", e.target.value as "camp" | "clinic" | "private")}>
                <option value="camp">Camp</option>
                <option value="clinic">Clinic</option>
                <option value="private">Private</option>
              </select>
            </div>
            <div>
              <label className="block text-xs font-medium text-[var(--text-secondary)] mb-1">Skill Level</label>
              <select className="input w-full" value={form.skill_level} onChange={(e) => set("skill_level", e.target.value)}>
                <option value="beginner">Beginner</option>
                <option value="intermediate">Intermediate</option>
                <option value="advanced">Advanced</option>
                <option value="elite">Elite</option>
              </select>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-medium text-[var(--text-secondary)] mb-1">Start Date *</label>
              <input
                type="date"
                className="input w-full"
                value={form.start_date}
                onChange={(e) => set("start_date", e.target.value)}
              />
              {errors.start_date && <p className="text-xs text-accent-rose mt-1">{errors.start_date}</p>}
            </div>
            <div>
              <label className="block text-xs font-medium text-[var(--text-secondary)] mb-1">End Date</label>
              <input
                type="date"
                className="input w-full"
                value={form.end_date}
                onChange={(e) => set("end_date", e.target.value)}
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-medium text-[var(--text-secondary)] mb-1">Start Time *</label>
              <input
                type="time"
                className="input w-full"
                value={form.start_time}
                onChange={(e) => set("start_time", e.target.value)}
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-[var(--text-secondary)] mb-1">End Time *</label>
              <input
                type="time"
                className="input w-full"
                value={form.end_time}
                onChange={(e) => set("end_time", e.target.value)}
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-medium text-[var(--text-secondary)] mb-1">Capacity *</label>
              <input
                type="number"
                min="1"
                className="input w-full"
                value={form.capacity}
                onChange={(e) => set("capacity", parseInt(e.target.value) || 1)}
              />
              {errors.capacity && <p className="text-xs text-accent-rose mt-1">{errors.capacity}</p>}
            </div>
            <div>
              <label className="block text-xs font-medium text-[var(--text-secondary)] mb-1">Base Price ($) *</label>
              <input
                type="number"
                min="0"
                step="5"
                className="input w-full"
                value={form.base_price}
                onChange={(e) => set("base_price", parseFloat(e.target.value) || 0)}
              />
              {errors.base_price && <p className="text-xs text-accent-rose mt-1">{errors.base_price}</p>}
            </div>
          </div>

          <div>
            <label className="block text-xs font-medium text-[var(--text-secondary)] mb-1">Location</label>
            <input
              className="input w-full"
              value={form.location}
              onChange={(e) => set("location", e.target.value)}
              placeholder="Field 1, Court 3, etc."
            />
          </div>

          <div className="flex gap-3 pt-2">
            <button type="button" onClick={onClose} className="btn-secondary flex-1">
              Cancel
            </button>
            <button
              type="submit"
              disabled={createEvent.isPending}
              className="btn-primary flex-1"
            >
              {createEvent.isPending ? "Creating…" : "Create Event"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

function ImportModal({ onClose }: { onClose: () => void }) {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const toast = useToast();

  const handleImport = async () => {
    if (!file) return;
    setLoading(true);
    try {
      await api.importEvents(file);
      toast.success("Events imported successfully");
      onClose();
    } catch {
      toast.error("Import failed. Check your CSV format and try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
      <div className="w-full max-w-md bg-[var(--bg-card)] rounded-2xl border border-[var(--border-subtle)] shadow-2xl">
        <div className="flex items-center justify-between px-6 py-4 border-b border-[var(--border-subtle)]">
          <h2 className="font-display text-lg font-semibold">Import Events</h2>
          <button onClick={onClose} className="p-1.5 rounded-lg hover:bg-[var(--bg-secondary)] text-[var(--text-muted)]">
            <X className="w-4 h-4" />
          </button>
        </div>
        <div className="p-6 space-y-4">
          <p className="text-sm text-[var(--text-secondary)]">
            Upload a CSV file with columns: title, event_type, start_date, capacity, base_price
          </p>
          <div
            className="border-2 border-dashed border-[var(--border-subtle)] rounded-xl p-8 text-center cursor-pointer hover:border-erebys-500/40 transition-colors"
            onClick={() => document.getElementById("csv-upload")?.click()}
          >
            <Upload className="w-8 h-8 text-[var(--text-muted)] mx-auto mb-2" />
            <p className="text-sm text-[var(--text-secondary)]">
              {file ? file.name : "Click to select CSV file"}
            </p>
            <input
              id="csv-upload"
              type="file"
              accept=".csv"
              className="hidden"
              onChange={(e) => setFile(e.target.files?.[0] || null)}
            />
          </div>
          <div className="flex gap-3">
            <button onClick={onClose} className="btn-secondary flex-1">Cancel</button>
            <button
              onClick={handleImport}
              disabled={!file || loading}
              className="btn-primary flex-1"
            >
              {loading ? "Importing…" : "Import"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function EventsPage() {
  const { data: events, isLoading } = useEvents();
  const [showNewEvent, setShowNewEvent] = useState(false);
  const [showImport, setShowImport] = useState(false);
  const toast = useToast();

  const handleExport = async () => {
    try {
      const { data } = await api.exportEvents();
      const blob = new Blob([data], { type: "text/csv" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "event_performance.csv";
      a.click();
    } catch {
      toast.error("Export failed. Please try again.");
    }
  };

  const columns = [
    {
      key: "title",
      label: "Event",
      render: (e: Event) => (
        <div>
          <p className="font-medium">{e.title}</p>
          <p className="text-xs text-[var(--text-muted)] capitalize mt-0.5">
            {e.event_type} · {e.skill_level}
          </p>
        </div>
      ),
    },
    {
      key: "status",
      label: "Status",
      render: (e: Event) => <StatusBadge status={e.status} />,
    },
    {
      key: "current_price",
      label: "Price",
      sortable: true,
      align: "right" as const,
      render: (e: Event) => (
        <span className="font-mono">{formatCurrency(e.current_price)}</span>
      ),
    },
    {
      key: "booked_count",
      label: "Bookings",
      sortable: true,
      align: "right" as const,
      render: (e: Event) => (
        <span className="font-mono">
          {e.booked_count}/{e.capacity}
        </span>
      ),
    },
    {
      key: "utilization",
      label: "Utilization",
      sortable: true,
      align: "right" as const,
      render: (e: Event) => {
        const pct = e.capacity > 0 ? (e.booked_count / e.capacity) * 100 : 0;
        const color =
          pct >= 80
            ? "text-accent-emerald"
            : pct >= 50
              ? "text-accent-amber"
              : "text-accent-rose";
        return <span className={`font-mono ${color}`}>{pct.toFixed(0)}%</span>;
      },
    },
    {
      key: "start_date",
      label: "Date",
      sortable: true,
      render: (e: Event) => (
        <span className="text-[var(--text-secondary)]">
          {formatDate(e.start_date)}
        </span>
      ),
    },
  ];

  if (isLoading) return <PageLoader />;

  return (
    <>
      {showNewEvent && <NewEventModal onClose={() => setShowNewEvent(false)} />}
      {showImport && <ImportModal onClose={() => setShowImport(false)} />}

      <div className="space-y-6 animate-fade-in">
        <PageHeader
          title="Events"
          description={`${events?.length ?? 0} events across all types`}
          actions={
            <div className="flex gap-2">
              <button onClick={handleExport} className="btn-secondary flex items-center gap-2">
                <Download className="w-4 h-4" />
                Export CSV
              </button>
              <button onClick={() => setShowImport(true)} className="btn-secondary flex items-center gap-2">
                <Upload className="w-4 h-4" />
                Import
              </button>
              <button onClick={() => setShowNewEvent(true)} className="btn-primary flex items-center gap-2">
                <Plus className="w-4 h-4" />
                New Event
              </button>
            </div>
          }
        />

        <DataTable columns={columns} data={(events as Event[]) ?? []} />
      </div>
    </>
  );
}
