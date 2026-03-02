"use client";

import { useState } from "react";
import {
  PageHeader,
  Card,
  EmptyState,
  PageLoader,
  StatusBadge,
  Spinner,
} from "@/components/ui/shared";
import { EvaluationRadarChart } from "@/components/charts/RadarChart";
import {
  useEvaluations,
  useEvaluationStats,
  useEvaluationTemplates,
  useEvaluation,
  useCreateEvaluation,
  useGenerateNarrative,
  usePublishEvaluation,
} from "@/hooks/use-evaluations";
import {
  ClipboardList,
  TrendingUp,
  TrendingDown,
  Minus,
  Sparkles,
  Eye,
  Send,
  Plus,
  X,
} from "lucide-react";

interface EvaluationListItem {
  id: string;
  athlete_id: string;
  athlete_name: string;
  coach_id: string | null;
  coach_name: string | null;
  evaluation_type: string;
  period_start: string;
  period_end: string;
  overall_score: number;
  status: string;
  ai_generated: boolean;
  created_at: string;
  category_count: number;
}

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

interface EvaluationTemplate {
  id: string;
  organization_id: string | null;
  sport_type: string;
  name: string;
  categories: { name: string; weight: number }[];
  is_default: boolean;
}

interface EvalStats {
  total: number;
  drafts: number;
  published: number;
  ai_generated: number;
  this_month: number;
  athletes_evaluated: number;
}

function scoreColor(score: number) {
  if (score >= 8) return "text-[var(--accent-emerald)]";
  if (score >= 6) return "text-[var(--accent-amber)]";
  return "text-[var(--accent-rose)]";
}

function TrendIcon({ trend }: { trend: string }) {
  if (trend === "improving")
    return <TrendingUp size={14} className="text-[var(--accent-emerald)]" />;
  if (trend === "declining")
    return <TrendingDown size={14} className="text-[var(--accent-rose)]" />;
  return <Minus size={14} className="text-[var(--text-muted)]" />;
}

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

function initials(name: string) {
  return name
    .split(" ")
    .map((n) => n[0])
    .join("")
    .toUpperCase()
    .slice(0, 2);
}

function TypeBadge({ type }: { type: string }) {
  const colorMap: Record<string, string> = {
    session: "bg-[rgba(6,182,212,0.12)] text-[var(--accent-cyan)]",
    monthly: "bg-[rgba(92,124,250,0.12)] text-[var(--accent-blue)]",
    quarterly: "bg-[rgba(245,158,11,0.12)] text-[var(--accent-amber)]",
  };
  const cls = colorMap[type] ?? "bg-[rgba(139,158,194,0.12)] text-[var(--text-secondary)]";
  return (
    <span className={`badge capitalize ${cls}`}>{type}</span>
  );
}

function ViewEvaluationModal({
  evalId,
  onClose,
}: {
  evalId: string;
  onClose: () => void;
}) {
  const { data: evaluation, isLoading } = useEvaluation(evalId);
  const generateNarrative = useGenerateNarrative();
  const publishEvaluation = usePublishEvaluation();

  const ev = evaluation as EvaluationResponse | undefined;

  const radarData =
    ev?.categories.map((c) => ({
      category: c.category_name,
      score: c.score,
      previousScore: c.previous_score ?? undefined,
    })) ?? [];

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm"
      onClick={(e) => e.target === e.currentTarget && onClose()}
    >
      <div className="relative bg-[var(--bg-card)] border border-[var(--border-subtle)] rounded-2xl p-6 max-w-2xl w-full max-h-[90vh] overflow-y-auto mx-4">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 p-1 rounded-lg text-[var(--text-muted)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-secondary)] transition-colors"
        >
          <X size={18} />
        </button>

        {isLoading || !ev ? (
          <div className="flex items-center justify-center py-20">
            <Spinner size="lg" />
          </div>
        ) : (
          <div className="space-y-6">
            <div>
              <div className="flex items-start justify-between gap-4 mb-2">
                <div>
                  <h2 className="font-display text-xl font-bold">
                    {ev.athlete_name ?? ev.athlete_id}
                  </h2>
                  <p className="text-sm text-[var(--text-secondary)] mt-0.5">
                    {ev.coach_name ? `Coach: ${ev.coach_name}` : "No coach assigned"}
                  </p>
                </div>
                <StatusBadge status={ev.status} />
              </div>
              <div className="flex items-center gap-3 flex-wrap">
                <TypeBadge type={ev.evaluation_type} />
                <span className="text-xs text-[var(--text-muted)]">
                  {formatDate(ev.period_start)} &rarr; {formatDate(ev.period_end)}
                </span>
                {ev.ai_generated && (
                  <span className="flex items-center gap-1 text-xs text-[var(--accent-cyan)]">
                    <Sparkles size={11} />
                    AI Generated
                  </span>
                )}
              </div>
            </div>

            <div className="text-center">
              <p className="text-xs text-[var(--text-muted)] mb-1">Overall Score</p>
              <p className={`font-display text-5xl font-bold ${scoreColor(ev.overall_score)}`}>
                {ev.overall_score.toFixed(1)}
                <span className="text-xl text-[var(--text-muted)] font-normal">/10</span>
              </p>
            </div>

            {ev.categories.length > 0 && (
              <div>
                <h3 className="font-display text-sm font-semibold mb-3">
                  Performance Radar
                </h3>
                <EvaluationRadarChart data={radarData} />
              </div>
            )}

            {ev.categories.length > 0 && (
              <div>
                <h3 className="font-display text-sm font-semibold mb-3">
                  Category Breakdown
                </h3>
                <div className="space-y-3">
                  {ev.categories
                    .sort((a, b) => a.display_order - b.display_order)
                    .map((cat) => (
                      <div key={cat.id} className="space-y-1">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            <TrendIcon trend={cat.trend} />
                            <span className="text-sm font-medium">
                              {cat.category_name}
                            </span>
                          </div>
                          <span className={`font-mono text-sm font-bold ${scoreColor(cat.score)}`}>
                            {cat.score.toFixed(1)}/10
                          </span>
                        </div>
                        <div className="h-1.5 rounded-full bg-[var(--bg-secondary)] overflow-hidden">
                          <div
                            className="h-full rounded-full transition-all"
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
                        {cat.notes && (
                          <p className="text-xs text-[var(--text-muted)] pl-5">
                            {cat.notes}
                          </p>
                        )}
                      </div>
                    ))}
                </div>
              </div>
            )}

            {ev.coach_notes && (
              <div>
                <h3 className="font-display text-sm font-semibold mb-2">
                  Coach Notes
                </h3>
                <p className="text-sm text-[var(--text-secondary)] leading-relaxed">
                  {ev.coach_notes}
                </p>
              </div>
            )}

            {ev.narrative ? (
              <div className="space-y-4">
                <h3 className="font-display text-sm font-semibold">
                  AI Narrative
                </h3>
                <p className="text-sm text-[var(--text-secondary)] leading-relaxed">
                  {ev.narrative.summary}
                </p>

                {ev.narrative.strengths.length > 0 && (
                  <div>
                    <p className="text-xs font-semibold text-[var(--accent-emerald)] mb-1.5 uppercase tracking-wider">
                      Strengths
                    </p>
                    <ul className="space-y-1">
                      {ev.narrative.strengths.map((s, i) => (
                        <li key={i} className="flex items-start gap-2 text-sm text-[var(--text-secondary)]">
                          <span className="text-[var(--accent-emerald)] mt-0.5">+</span>
                          {s}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {ev.narrative.areas_for_improvement.length > 0 && (
                  <div>
                    <p className="text-xs font-semibold text-[var(--accent-amber)] mb-1.5 uppercase tracking-wider">
                      Areas for Improvement
                    </p>
                    <ul className="space-y-1">
                      {ev.narrative.areas_for_improvement.map((a, i) => (
                        <li key={i} className="flex items-start gap-2 text-sm text-[var(--text-secondary)]">
                          <span className="text-[var(--accent-amber)] mt-0.5">&bull;</span>
                          {a}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {ev.narrative.recommendations.length > 0 && (
                  <div>
                    <p className="text-xs font-semibold text-[var(--accent-blue)] mb-1.5 uppercase tracking-wider">
                      Recommendations
                    </p>
                    <ul className="space-y-1">
                      {ev.narrative.recommendations.map((r, i) => (
                        <li key={i} className="flex items-start gap-2 text-sm text-[var(--text-secondary)]">
                          <span className="text-[var(--accent-blue)] mt-0.5">&rarr;</span>
                          {r}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {ev.narrative.parent_friendly_summary && (
                  <div className="p-4 rounded-xl bg-[rgba(6,182,212,0.08)] border border-[rgba(6,182,212,0.2)]">
                    <p className="text-xs font-semibold text-[var(--accent-cyan)] mb-1.5 uppercase tracking-wider">
                      Parent Summary
                    </p>
                    <p className="text-sm text-[var(--text-secondary)] leading-relaxed">
                      {ev.narrative.parent_friendly_summary}
                    </p>
                  </div>
                )}
              </div>
            ) : (
              ev.status === "draft" && (
                <div className="p-4 rounded-xl bg-[var(--bg-secondary)] border border-[var(--border-subtle)] text-center">
                  <p className="text-sm text-[var(--text-muted)] mb-3">
                    No AI narrative generated yet.
                  </p>
                  <button
                    className="btn-primary flex items-center gap-2 mx-auto"
                    onClick={() => generateNarrative.mutate(ev.id)}
                    disabled={generateNarrative.isPending}
                  >
                    {generateNarrative.isPending ? (
                      <Spinner size="sm" />
                    ) : (
                      <Sparkles size={15} />
                    )}
                    Generate AI Narrative
                  </button>
                </div>
              )
            )}

            {ev.status === "draft" && (
              <div className="flex justify-end pt-2 border-t border-[var(--border-subtle)]">
                <button
                  className="btn-primary flex items-center gap-2"
                  onClick={() => publishEvaluation.mutate(ev.id)}
                  disabled={publishEvaluation.isPending}
                >
                  {publishEvaluation.isPending ? (
                    <Spinner size="sm" />
                  ) : (
                    <Send size={15} />
                  )}
                  Publish Evaluation
                </button>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

function NewEvaluationModal({
  onClose,
}: {
  onClose: () => void;
}) {
  const { data: templates } = useEvaluationTemplates();
  const createEvaluation = useCreateEvaluation();

  const [templateId, setTemplateId] = useState("");
  const [athleteId, setAthleteId] = useState("");
  const [coachId, setCoachId] = useState("");
  const [evalType, setEvalType] = useState("session");
  const [periodStart, setPeriodStart] = useState("");
  const [periodEnd, setPeriodEnd] = useState("");
  const [notes, setNotes] = useState("");
  const [categoryScores, setCategoryScores] = useState<Record<string, number>>({});

  const templateList = (templates as EvaluationTemplate[]) ?? [];
  const selectedTemplate = templateList.find((t) => t.id === templateId);

  function handleTemplateChange(id: string) {
    setTemplateId(id);
    const tmpl = templateList.find((t) => t.id === id);
    if (tmpl) {
      const defaults: Record<string, number> = {};
      tmpl.categories.forEach((c) => {
        defaults[c.name] = 5;
      });
      setCategoryScores(defaults);
    }
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const categories = selectedTemplate?.categories.map((c) => ({
      category_name: c.name,
      score: categoryScores[c.name] ?? 5,
      weight: c.weight,
    })) ?? [];

    await createEvaluation.mutateAsync({
      template_id: templateId || undefined,
      athlete_id: athleteId,
      coach_id: coachId || undefined,
      evaluation_type: evalType,
      period_start: periodStart,
      period_end: periodEnd,
      coach_notes: notes || undefined,
      categories,
    });
    onClose();
  }

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm"
      onClick={(e) => e.target === e.currentTarget && onClose()}
    >
      <div className="relative bg-[var(--bg-card)] border border-[var(--border-subtle)] rounded-2xl p-6 max-w-2xl w-full max-h-[90vh] overflow-y-auto mx-4">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 p-1 rounded-lg text-[var(--text-muted)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-secondary)] transition-colors"
        >
          <X size={18} />
        </button>

        <h2 className="font-display text-xl font-bold mb-6">New Evaluation</h2>

        <form onSubmit={handleSubmit} className="space-y-5">
          <div>
            <label className="block text-xs font-semibold text-[var(--text-secondary)] mb-1.5 uppercase tracking-wider">
              Template
            </label>
            <select
              className="input-field w-full"
              value={templateId}
              onChange={(e) => handleTemplateChange(e.target.value)}
            >
              <option value="">No template (manual)</option>
              {templateList.map((t) => (
                <option key={t.id} value={t.id}>
                  {t.sport_type} &mdash; {t.name}
                  {t.is_default ? " (Default)" : ""}
                </option>
              ))}
            </select>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-[var(--text-secondary)] mb-1.5 uppercase tracking-wider">
                Athlete ID
              </label>
              <input
                type="text"
                className="input-field w-full"
                placeholder="e.g. ath_123"
                value={athleteId}
                onChange={(e) => setAthleteId(e.target.value)}
                required
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-[var(--text-secondary)] mb-1.5 uppercase tracking-wider">
                Coach ID
              </label>
              <input
                type="text"
                className="input-field w-full"
                placeholder="e.g. coa_456"
                value={coachId}
                onChange={(e) => setCoachId(e.target.value)}
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-[var(--text-secondary)] mb-1.5 uppercase tracking-wider">
              Evaluation Type
            </label>
            <div className="flex gap-3">
              {["session", "monthly", "quarterly"].map((type) => (
                <label
                  key={type}
                  className={`flex items-center gap-2 px-4 py-2 rounded-lg border cursor-pointer transition-colors capitalize text-sm ${
                    evalType === type
                      ? "border-[var(--accent-blue)] bg-[rgba(92,124,250,0.1)] text-[var(--accent-blue)]"
                      : "border-[var(--border-subtle)] text-[var(--text-secondary)] hover:border-[rgba(91,124,250,0.3)]"
                  }`}
                >
                  <input
                    type="radio"
                    name="eval_type"
                    value={type}
                    checked={evalType === type}
                    onChange={() => setEvalType(type)}
                    className="hidden"
                  />
                  {type}
                </label>
              ))}
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-[var(--text-secondary)] mb-1.5 uppercase tracking-wider">
                Period Start
              </label>
              <input
                type="date"
                className="input-field w-full"
                value={periodStart}
                onChange={(e) => setPeriodStart(e.target.value)}
                required
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-[var(--text-secondary)] mb-1.5 uppercase tracking-wider">
                Period End
              </label>
              <input
                type="date"
                className="input-field w-full"
                value={periodEnd}
                onChange={(e) => setPeriodEnd(e.target.value)}
                required
              />
            </div>
          </div>

          {selectedTemplate && selectedTemplate.categories.length > 0 && (
            <div>
              <label className="block text-xs font-semibold text-[var(--text-secondary)] mb-3 uppercase tracking-wider">
                Category Scores
              </label>
              <div className="space-y-4">
                {selectedTemplate.categories.map((cat) => {
                  const val = categoryScores[cat.name] ?? 5;
                  return (
                    <div key={cat.name}>
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-sm text-[var(--text-primary)]">
                          {cat.name}
                        </span>
                        <span className={`font-mono text-sm font-bold ${scoreColor(val)}`}>
                          {val.toFixed(1)}/10
                        </span>
                      </div>
                      <input
                        type="range"
                        min={0}
                        max={10}
                        step={0.5}
                        value={val}
                        onChange={(e) =>
                          setCategoryScores((prev) => ({
                            ...prev,
                            [cat.name]: parseFloat(e.target.value),
                          }))
                        }
                        className="w-full accent-[var(--accent-cyan)]"
                      />
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          <div>
            <label className="block text-xs font-semibold text-[var(--text-secondary)] mb-1.5 uppercase tracking-wider">
              Coach Notes
            </label>
            <textarea
              className="input-field w-full resize-none"
              rows={3}
              placeholder="Overall observations, context, notes..."
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
            />
          </div>

          <div className="flex justify-end gap-3 pt-2 border-t border-[var(--border-subtle)]">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-sm rounded-lg border border-[var(--border-subtle)] text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:border-[rgba(91,124,250,0.3)] transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="btn-primary flex items-center gap-2"
              disabled={createEvaluation.isPending}
            >
              {createEvaluation.isPending ? <Spinner size="sm" /> : <Plus size={15} />}
              Create Draft
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

const FILTERS = [
  { label: "All", value: "all" },
  { label: "Drafts", value: "draft" },
  { label: "Published", value: "published" },
];

export default function EvaluationsPage() {
  const [activeFilter, setActiveFilter] = useState("all");
  const [viewingId, setViewingId] = useState<string | null>(null);
  const [newModalOpen, setNewModalOpen] = useState(false);

  const { data: evaluations, isLoading } = useEvaluations(
    activeFilter === "all" ? undefined : { status: activeFilter }
  );
  const { data: stats } = useEvaluationStats();

  const evalList = (evaluations as EvaluationListItem[]) ?? [];
  const evalStats = stats as EvalStats | undefined;

  const generateNarrative = useGenerateNarrative();
  const publishEvaluation = usePublishEvaluation();

  return (
    <div className="space-y-6 animate-fade-in">
      <PageHeader
        title="Evaluations"
        description="Create, manage, and publish athlete performance evaluations"
        actions={
          <button
            className="btn-primary flex items-center gap-2"
            onClick={() => setNewModalOpen(true)}
          >
            <Plus size={16} />
            New Evaluation
          </button>
        }
      />

      {evalStats && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[
            { label: "Total", value: evalStats.total, color: "text-[var(--text-primary)]" },
            { label: "Drafts", value: evalStats.drafts, color: "text-[var(--accent-amber)]" },
            { label: "Published", value: evalStats.published, color: "text-[var(--accent-emerald)]" },
            { label: "Athletes Evaluated", value: evalStats.athletes_evaluated, color: "text-[var(--accent-cyan)]" },
          ].map((kpi) => (
            <div
              key={kpi.label}
              className="card-glass rounded-xl p-4"
            >
              <p className="text-xs text-[var(--text-muted)] mb-1">{kpi.label}</p>
              <p className={`font-display text-3xl font-bold ${kpi.color}`}>
                {kpi.value}
              </p>
            </div>
          ))}
        </div>
      )}

      <Card>
        <div className="flex items-center gap-1 mb-6 p-1 bg-[var(--bg-secondary)] rounded-lg w-fit">
          {FILTERS.map((f) => (
            <button
              key={f.value}
              onClick={() => setActiveFilter(f.value)}
              className={`px-4 py-1.5 rounded-md text-sm font-medium transition-colors ${
                activeFilter === f.value
                  ? "bg-[var(--bg-card)] text-[var(--text-primary)] shadow-sm"
                  : "text-[var(--text-muted)] hover:text-[var(--text-secondary)]"
              }`}
            >
              {f.label}
            </button>
          ))}
        </div>

        {isLoading ? (
          <PageLoader />
        ) : evalList.length === 0 ? (
          <EmptyState
            icon={<ClipboardList size={40} />}
            title="No evaluations found"
            description="Create your first evaluation using the button above."
          />
        ) : (
          <div className="space-y-2">
            {evalList.map((ev) => (
              <div
                key={ev.id}
                className="flex items-center gap-4 p-4 rounded-xl bg-[var(--bg-secondary)] hover:bg-[rgba(19,31,53,0.9)] transition-colors"
              >
                <div className="w-10 h-10 rounded-full bg-[rgba(92,124,250,0.15)] border border-[rgba(92,124,250,0.2)] flex items-center justify-center text-xs font-bold text-[var(--accent-blue)] flex-shrink-0">
                  {initials(ev.athlete_name)}
                </div>

                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 flex-wrap mb-0.5">
                    <span className="font-medium text-sm truncate">
                      {ev.athlete_name}
                    </span>
                    <TypeBadge type={ev.evaluation_type} />
                    {ev.ai_generated && (
                      <span className="flex items-center gap-1 text-xs text-[var(--accent-cyan)]">
                        <Sparkles size={11} />
                        AI
                      </span>
                    )}
                  </div>
                  <p className="text-xs text-[var(--text-muted)]">
                    {formatDate(ev.period_start)} &rarr; {formatDate(ev.period_end)}
                    {ev.category_count > 0 && (
                      <span className="ml-2">&middot; {ev.category_count} categories</span>
                    )}
                  </p>
                </div>

                <div className="text-right flex-shrink-0">
                  <p className={`font-display text-2xl font-bold leading-none ${scoreColor(ev.overall_score)}`}>
                    {ev.overall_score.toFixed(1)}
                    <span className="text-xs text-[var(--text-muted)] font-normal ml-0.5">/10</span>
                  </p>
                </div>

                <div className="flex-shrink-0">
                  <StatusBadge status={ev.status} />
                </div>

                <div className="flex items-center gap-2 flex-shrink-0">
                  <button
                    className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-[var(--border-subtle)] text-xs text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:border-[rgba(91,124,250,0.3)] transition-colors"
                    onClick={() => setViewingId(ev.id)}
                  >
                    <Eye size={13} />
                    View
                  </button>

                  {ev.status === "draft" && (
                    <button
                      className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-[rgba(6,182,212,0.3)] text-xs text-[var(--accent-cyan)] hover:bg-[rgba(6,182,212,0.08)] transition-colors"
                      onClick={() => generateNarrative.mutate(ev.id)}
                      disabled={generateNarrative.isPending && generateNarrative.variables === ev.id}
                    >
                      {generateNarrative.isPending && generateNarrative.variables === ev.id ? (
                        <Spinner size="sm" />
                      ) : (
                        <Sparkles size={13} />
                      )}
                      AI Narrative
                    </button>
                  )}

                  {ev.status === "draft" && (
                    <button
                      className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-[rgba(16,185,129,0.3)] text-xs text-[var(--accent-emerald)] hover:bg-[rgba(16,185,129,0.08)] transition-colors"
                      onClick={() => publishEvaluation.mutate(ev.id)}
                      disabled={publishEvaluation.isPending && publishEvaluation.variables === ev.id}
                    >
                      {publishEvaluation.isPending && publishEvaluation.variables === ev.id ? (
                        <Spinner size="sm" />
                      ) : (
                        <Send size={13} />
                      )}
                      Publish
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </Card>

      {viewingId && (
        <ViewEvaluationModal
          evalId={viewingId}
          onClose={() => setViewingId(null)}
        />
      )}

      {newModalOpen && (
        <NewEvaluationModal onClose={() => setNewModalOpen(false)} />
      )}
    </div>
  );
}
