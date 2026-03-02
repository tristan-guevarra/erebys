"use client";

import { useState } from "react";
import { PageHeader, Card, EmptyState, PageLoader } from "@/components/ui/shared";
import { EvaluationRadarChart } from "@/components/charts/RadarChart";
import { useAthleteEvaluations } from "@/hooks/use-evaluations";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { Search, Star } from "lucide-react";

interface CategoryResponse {
  id: string;
  category_name: string;
  score: number;
  previous_score: number | null;
  trend: string;
  notes: string | null;
  display_order: number;
  weight: number;
}

interface NarrativeResponse {
  id: string;
  summary: string;
  strengths: string[];
  areas_for_improvement: string[];
  recommendations: string[];
  parent_friendly_summary: string;
}

interface EvaluationResponse {
  id: string;
  organization_id: string;
  athlete_id: string;
  coach_id: string | null;
  evaluation_type: string;
  period_start: string;
  period_end: string;
  overall_score: number;
  status: string;
  ai_generated: boolean;
  coach_notes: string | null;
  created_at: string;
  updated_at: string;
  categories: CategoryResponse[];
  narrative: NarrativeResponse | null;
  athlete_name: string | null;
  coach_name: string | null;
}

function scoreColor(score: number) {
  if (score >= 8) return "text-[var(--accent-emerald)]";
  if (score >= 6) return "text-[var(--accent-amber)]";
  return "text-[var(--accent-rose)]";
}

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

function formatDateShort(dateStr: string) {
  return new Date(dateStr).toLocaleDateString("en-US", {
    month: "short",
    year: "2-digit",
  });
}

function TypeBadge({ type }: { type: string }) {
  const colorMap: Record<string, string> = {
    session: "bg-[rgba(6,182,212,0.12)] text-[var(--accent-cyan)]",
    monthly: "bg-[rgba(92,124,250,0.12)] text-[var(--accent-blue)]",
    quarterly: "bg-[rgba(245,158,11,0.12)] text-[var(--accent-amber)]",
  };
  const cls =
    colorMap[type] ??
    "bg-[rgba(139,158,194,0.12)] text-[var(--text-secondary)]";
  return <span className={`badge capitalize ${cls}`}>{type}</span>;
}

export default function MyProgressPage() {
  const [inputValue, setInputValue] = useState("");
  const [athleteId, setAthleteId] = useState("");

  const { data: evaluations, isLoading } = useAthleteEvaluations(athleteId);

  const evalList = ((evaluations as EvaluationResponse[]) ?? []).sort(
    (a, b) =>
      new Date(b.period_start).getTime() - new Date(a.period_start).getTime()
  );

  const progressData = [...evalList]
    .reverse()
    .map((ev) => ({
      date: formatDateShort(ev.period_start),
      score: ev.overall_score,
      type: ev.evaluation_type,
    }));

  function handleLoad(e: React.FormEvent) {
    e.preventDefault();
    setAthleteId(inputValue.trim());
  }

  return (
    <div className="space-y-6 animate-fade-in">
      <PageHeader
        title="Athlete Progress"
        description="Track individual athlete development over time"
      />

      <Card>
        <form onSubmit={handleLoad} className="flex items-center gap-3">
          <div className="relative flex-1 max-w-sm">
            <Search
              size={15}
              className="absolute left-3 top-1/2 -translate-y-1/2 text-[var(--text-muted)]"
            />
            <input
              type="text"
              className="input-field w-full pl-9"
              placeholder="Enter athlete ID..."
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
            />
          </div>
          <button
            type="submit"
            className="btn-primary"
            disabled={!inputValue.trim()}
          >
            Load
          </button>
        </form>
      </Card>

      {isLoading && <PageLoader />}

      {!isLoading && athleteId && evalList.length === 0 && (
        <EmptyState
          icon={<Star size={40} />}
          title="No evaluations found"
          description="No published evaluations exist for this athlete ID yet."
        />
      )}

      {!isLoading && evalList.length >= 2 && (
        <Card title="Score Progression">
          <ResponsiveContainer width="100%" height={200}>
            <AreaChart
              data={progressData}
              margin={{ top: 5, right: 10, left: 0, bottom: 0 }}
            >
              <defs>
                <linearGradient id="scoreGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#06b6d4" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#06b6d4" stopOpacity={0} />
                </linearGradient>
              </defs>
              <XAxis
                dataKey="date"
                tick={{ fill: "#5a6d8f", fontSize: 11 }}
                tickLine={false}
                axisLine={false}
              />
              <YAxis
                domain={[0, 10]}
                tick={{ fill: "#5a6d8f", fontSize: 11 }}
                tickLine={false}
                axisLine={false}
              />
              <Tooltip
                contentStyle={{
                  background: "#131f35",
                  border: "1px solid rgba(91,124,250,0.2)",
                  borderRadius: 8,
                  fontSize: 12,
                  color: "#e8ecf4",
                }}
                formatter={(value: number) => [`${value.toFixed(1)}/10`, "Score"]}
              />
              <Area
                type="monotone"
                dataKey="score"
                stroke="#06b6d4"
                strokeWidth={2}
                fill="url(#scoreGrad)"
                dot={{ fill: "#06b6d4", r: 4, strokeWidth: 0 }}
                activeDot={{ r: 6 }}
              />
            </AreaChart>
          </ResponsiveContainer>
        </Card>
      )}

      {!isLoading && evalList.length > 0 && (
        <div className="space-y-4">
          {evalList.map((ev) => (
            <Card key={ev.id}>
              <div className="space-y-4">
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <div className="flex items-center gap-2 mb-1 flex-wrap">
                      <TypeBadge type={ev.evaluation_type} />
                      <span className="text-xs text-[var(--text-muted)]">
                        {formatDate(ev.period_start)} &rarr;{" "}
                        {formatDate(ev.period_end)}
                      </span>
                    </div>
                    {ev.coach_name && (
                      <p className="text-xs text-[var(--text-muted)]">
                        Coach: {ev.coach_name}
                      </p>
                    )}
                  </div>
                  <div className="text-right flex-shrink-0">
                    <p className="text-xs text-[var(--text-muted)] mb-0.5">
                      Overall Score
                    </p>
                    <p
                      className={`font-display text-4xl font-bold leading-none ${scoreColor(ev.overall_score)}`}
                    >
                      {ev.overall_score.toFixed(1)}
                      <span className="text-sm text-[var(--text-muted)] font-normal ml-0.5">
                        /10
                      </span>
                    </p>
                  </div>
                </div>

                {ev.status === "published" && ev.categories.length > 0 && (
                  <EvaluationRadarChart
                    data={ev.categories.map((c) => ({
                      category: c.category_name,
                      score: c.score,
                      previousScore: c.previous_score ?? undefined,
                    }))}
                  />
                )}

                {ev.categories.length > 0 && (
                  <div className="grid grid-cols-2 gap-x-6 gap-y-2">
                    {ev.categories
                      .sort((a, b) => a.display_order - b.display_order)
                      .map((cat) => (
                        <div key={cat.id} className="space-y-1">
                          <div className="flex items-center justify-between">
                            <span className="text-xs text-[var(--text-secondary)] truncate mr-2">
                              {cat.category_name}
                            </span>
                            <span
                              className={`font-mono text-xs font-bold flex-shrink-0 ${scoreColor(cat.score)}`}
                            >
                              {cat.score.toFixed(1)}
                            </span>
                          </div>
                          <div className="h-1 rounded-full bg-[var(--bg-secondary)] overflow-hidden">
                            <div
                              className="h-full rounded-full"
                              style={{
                                width: `${(cat.score / 10) * 100}%`,
                                background:
                                  cat.score >= 8
                                    ? "var(--accent-emerald)"
                                    : cat.score >= 6
                                    ? "var(--accent-amber)"
                                    : "var(--accent-rose)",
                              }}
                            />
                          </div>
                        </div>
                      ))}
                  </div>
                )}

                {ev.narrative?.parent_friendly_summary && (
                  <div className="p-4 rounded-xl bg-[rgba(6,182,212,0.08)] border border-[rgba(6,182,212,0.2)]">
                    <p className="text-xs font-semibold text-[var(--accent-cyan)] mb-1.5 uppercase tracking-wider">
                      Summary
                    </p>
                    <p className="text-sm text-[var(--text-secondary)] leading-relaxed">
                      {ev.narrative.parent_friendly_summary}
                    </p>
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
