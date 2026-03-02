import { cn } from "@/lib/utils";
import { TrendingUp, TrendingDown, Minus } from "lucide-react";

interface KPICardProps {
  title: string;
  value: string;
  change?: number;
  suffix?: string;
  icon?: React.ReactNode;
  variant?: "default" | "success" | "warning" | "danger";
  className?: string;
}

export function KPICard({ title, value, change, suffix, icon, variant = "default", className }: KPICardProps) {
  const isPositive = (change ?? 0) > 0;
  const isNeutral  = change === undefined || change === 0;
  const isNegative = (change ?? 0) < 0;

  return (
    <div className={cn("kpi-card group", className)}>
      <div className="flex items-start justify-between mb-3">
        <span className="text-xs font-medium text-[var(--text-muted)] uppercase tracking-wider">
          {title}
        </span>
        {icon && (
          <span className="text-[var(--text-muted)] group-hover:text-erebys-400 transition-colors">
            {icon}
          </span>
        )}
      </div>

      <div className="flex items-end gap-1.5">
        <span className="font-display text-2xl font-bold tracking-tight text-[var(--text-primary)]">
          {value}
        </span>
        {suffix && (
          <span className="text-sm text-[var(--text-muted)] mb-0.5">{suffix}</span>
        )}
      </div>

      {change !== undefined && (
        <div className="mt-2 flex items-center gap-1.5">
          {isNeutral ? (
            <Minus className="w-3 h-3 text-[var(--text-muted)]" />
          ) : isPositive ? (
            <TrendingUp className="w-3 h-3 text-accent-emerald" />
          ) : (
            <TrendingDown className="w-3 h-3 text-accent-rose" />
          )}
          <span className={cn(
            "text-xs font-mono font-medium",
            isNeutral  && "text-[var(--text-muted)]",
            isPositive && "text-accent-emerald",
            isNegative && "text-accent-rose",
          )}>
            {isPositive ? "+" : ""}{change.toFixed(1)}%
          </span>
          <span className="text-xs text-[var(--text-muted)]">vs prev</span>
        </div>
      )}
    </div>
  );
}
