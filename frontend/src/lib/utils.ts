import { clsx, type ClassValue } from "clsx";

export function cn(...inputs: ClassValue[]) {
  return clsx(inputs);
}

export function formatCurrency(value: number): string {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(value);
}

export function formatPct(value: number, decimals = 1): string {
  return `${value >= 0 ? "+" : ""}${value.toFixed(decimals)}%`;
}

export function formatNumber(value: number): string {
  return new Intl.NumberFormat("en-US").format(value);
}

export function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

export function getStatusColor(status: string): string {
  const map: Record<string, string> = {
    published:  "text-accent-emerald",
    completed:  "text-erebys-400",
    full:       "text-accent-amber",
    cancelled:  "text-accent-rose",
    draft:      "text-[var(--text-muted)]",
    confirmed:  "text-accent-emerald",
    pending:    "text-accent-amber",
    running:    "text-accent-cyan",
    paused:     "text-accent-amber",
    applied:    "text-accent-emerald",
    approved:   "text-accent-emerald",
    rejected:   "text-accent-rose",
    archived:   "text-[var(--text-muted)]",
    low:        "text-accent-emerald",
    medium:     "text-accent-amber",
    high:       "text-accent-rose",
  };
  return map[status] || "text-[var(--text-muted)]";
}

export function getStatusBg(status: string): string {
  const map: Record<string, string> = {
    published:  "bg-emerald-500/10 border-emerald-500/20",
    completed:  "bg-violet-500/10 border-violet-500/20",
    full:       "bg-amber-500/10 border-amber-500/20",
    cancelled:  "bg-rose-500/10 border-rose-500/20",
    confirmed:  "bg-emerald-500/10 border-emerald-500/20",
    running:    "bg-cyan-500/10 border-cyan-500/20",
    draft:      "bg-white/5 border-white/10",
    archived:   "bg-white/5 border-white/10",
    pending:    "bg-amber-500/10 border-amber-500/20",
    low:        "bg-emerald-500/10 border-emerald-500/20",
    medium:     "bg-amber-500/10 border-amber-500/20",
    high:       "bg-rose-500/10 border-rose-500/20",
  };
  return map[status] || "bg-white/5 border-white/10";
}
