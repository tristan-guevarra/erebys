"use client";

import { useCoaches } from "@/hooks/use-data";
import { PageHeader, Card, PageLoader, EmptyState } from "@/components/ui/shared";
import { formatCurrency } from "@/lib/utils";
import { UserCircle2, Star, DollarSign } from "lucide-react";

interface Coach {
  id: string;
  full_name: string;
  email: string | null;
  specialty: string;
  hourly_rate: number;
  avg_rating: number;
  bio: string | null;
}

export default function CoachesPage() {
  const { data: coaches, isLoading } = useCoaches();

  if (isLoading) return <PageLoader />;

  const coachList = (coaches as Coach[]) ?? [];

  return (
    <div className="space-y-6 animate-fade-in">
      <PageHeader
        title="Coaches"
        description={`${coachList.length} coaches in your organization`}
      />

      {coachList.length === 0 ? (
        <Card>
          <EmptyState
            icon={<UserCircle2 className="w-10 h-10" />}
            title="No Coaches Yet"
            description="Add coaches to your organization to assign them to events."
          />
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {coachList.map((coach) => (
            <div key={coach.id} className="card-glass rounded-xl p-5 space-y-4">
              <div className="flex items-start gap-4">
                <div className="w-12 h-12 rounded-full bg-erebys-700 flex items-center justify-center text-sm font-bold text-erebys-300 shrink-0">
                  {coach.full_name
                    .split(" ")
                    .map((n) => n[0])
                    .join("")}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="font-display font-semibold truncate">{coach.full_name}</p>
                  {coach.email && (
                    <p className="text-xs text-[var(--text-muted)] truncate">{coach.email}</p>
                  )}
                  <p className="text-xs text-[var(--text-secondary)] capitalize mt-0.5">
                    {coach.specialty}
                  </p>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div className="p-3 rounded-lg bg-[var(--bg-secondary)] text-center">
                  <div className="flex items-center justify-center gap-1 mb-1">
                    <Star className="w-3.5 h-3.5 text-accent-amber" />
                    <span className="text-xs text-[var(--text-muted)]">Rating</span>
                  </div>
                  <p className="font-display text-lg font-bold">
                    {coach.avg_rating > 0 ? coach.avg_rating.toFixed(1) : "—"}
                  </p>
                </div>
                <div className="p-3 rounded-lg bg-[var(--bg-secondary)] text-center">
                  <div className="flex items-center justify-center gap-1 mb-1">
                    <DollarSign className="w-3.5 h-3.5 text-accent-emerald" />
                    <span className="text-xs text-[var(--text-muted)]">Rate</span>
                  </div>
                  <p className="font-display text-lg font-bold">
                    {coach.hourly_rate > 0 ? `${formatCurrency(coach.hourly_rate)}/hr` : "—"}
                  </p>
                </div>
              </div>

              {coach.bio && (
                <p className="text-xs text-[var(--text-secondary)] leading-relaxed line-clamp-2">
                  {coach.bio}
                </p>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
