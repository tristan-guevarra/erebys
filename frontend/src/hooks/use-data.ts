import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";

export function useOverviewKPIs(days = 30) {
  return useQuery({
    queryKey: ["overview-kpis", days],
    queryFn: () => api.getOverviewKPIs(days).then((r) => r.data),
  });
}

export function useRevenueByDay(days = 30) {
  return useQuery({
    queryKey: ["revenue-by-day", days],
    queryFn: () => api.getRevenueByDay(days).then((r) => r.data),
  });
}

export function useCohorts(months = 6) {
  return useQuery({
    queryKey: ["cohorts", months],
    queryFn: () => api.getCohorts(months).then((r) => r.data),
  });
}

export function useLTVDistribution() {
  return useQuery({
    queryKey: ["ltv-distribution"],
    queryFn: () => api.getLTVDistribution().then((r) => r.data),
  });
}

export function useNoShowRisks(limit = 20) {
  return useQuery({
    queryKey: ["no-show-risks", limit],
    queryFn: () => api.getNoShowRisks(limit).then((r) => r.data),
  });
}

export function useEvents() {
  return useQuery({
    queryKey: ["events"],
    queryFn: () => api.getEvents().then((r) => r.data),
  });
}

export function usePricingRecommendations(eventId?: string) {
  return useQuery({
    queryKey: ["pricing-recs", eventId],
    queryFn: () => api.getPricingRecommendations(eventId).then((r) => r.data),
  });
}

export function useGenerateRecommendation() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (eventId: string) =>
      api.generateRecommendation(eventId).then((r) => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["pricing-recs"] }),
  });
}

export function useWhatIfSimulate() {
  return useMutation({
    mutationFn: ({
      eventId,
      prices,
    }: {
      eventId: string;
      prices: number[];
    }) => api.whatIfSimulate(eventId, prices).then((r) => r.data),
  });
}

export function useChangeRequests(status?: string) {
  return useQuery({
    queryKey: ["change-requests", status],
    queryFn: () => api.getChangeRequests(status).then((r) => r.data),
  });
}

export function useApproveChangeRequest() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (requestId: string) =>
      api.approveChangeRequest(requestId).then((r) => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["change-requests"] }),
  });
}

export function useExperiments() {
  return useQuery({
    queryKey: ["experiments"],
    queryFn: () => api.getExperiments().then((r) => r.data),
  });
}

export function useAuditLogs(page = 1) {
  return useQuery({
    queryKey: ["audit-logs", page],
    queryFn: () => api.getAuditLogs(page).then((r) => r.data),
  });
}

export function useFeatureFlags() {
  return useQuery({
    queryKey: ["feature-flags"],
    queryFn: () => api.getFeatureFlags().then((r) => r.data),
  });
}

export function useInsights() {
  return useQuery({
    queryKey: ["insights"],
    queryFn: () => api.getInsights().then((r) => r.data),
  });
}

export function useGenerateInsight() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: () => api.generateInsight().then((r) => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["insights"] }),
  });
}

export function useCreateChangeRequest() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: { event_id: string; new_price: number; reason?: string; recommendation_id?: string }) =>
      api.createChangeRequest(data).then((r) => r.data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["change-requests"] });
      qc.invalidateQueries({ queryKey: ["events"] });
    },
  });
}

export function useCreateExperiment() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: Record<string, unknown>) =>
      api.createExperiment(data).then((r) => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["experiments"] }),
  });
}

export function useCoaches() {
  return useQuery({
    queryKey: ["coaches"],
    queryFn: () => api.getCoaches().then((r) => r.data),
  });
}

export function useCreateEvent() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: Record<string, unknown>) =>
      api.createEvent(data).then((r) => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["events"] }),
  });
}
