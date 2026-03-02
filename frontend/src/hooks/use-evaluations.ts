import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";

export function useEvaluations(params?: { status?: string; athlete_id?: string }) {
  return useQuery({
    queryKey: ["evaluations", params],
    queryFn: () => api.getEvaluations(params).then((r) => r.data),
  });
}

export function useEvaluationStats() {
  return useQuery({
    queryKey: ["evaluation-stats"],
    queryFn: () => api.getEvaluationStats().then((r) => r.data),
  });
}

export function useEvaluationTemplates() {
  return useQuery({
    queryKey: ["evaluation-templates"],
    queryFn: () => api.getEvaluationTemplates().then((r) => r.data),
  });
}

export function useEvaluation(evalId: string) {
  return useQuery({
    queryKey: ["evaluation", evalId],
    queryFn: () => api.getEvaluation(evalId).then((r) => r.data),
    enabled: !!evalId,
  });
}

export function useAthleteEvaluations(athleteId: string) {
  return useQuery({
    queryKey: ["athlete-evaluations", athleteId],
    queryFn: () => api.getAthleteEvaluations(athleteId).then((r) => r.data),
    enabled: !!athleteId,
  });
}

export function useCreateEvaluation() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: Record<string, unknown>) =>
      api.createEvaluation(data).then((r) => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["evaluations"] }),
  });
}

export function useGenerateNarrative() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (evalId: string) =>
      api.generateEvaluationNarrative(evalId).then((r) => r.data),
    onSuccess: (_, evalId) => {
      qc.invalidateQueries({ queryKey: ["evaluation", evalId] });
      qc.invalidateQueries({ queryKey: ["evaluations"] });
    },
  });
}

export function usePublishEvaluation() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (evalId: string) =>
      api.publishEvaluation(evalId).then((r) => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["evaluations"] }),
  });
}
