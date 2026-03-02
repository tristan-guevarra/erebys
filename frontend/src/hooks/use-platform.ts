import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";

export function usePlatformOverview() {
  return useQuery({
    queryKey: ["platform-overview"],
    queryFn: () => api.getPlatformOverview().then((r) => r.data),
  });
}

export function usePlatformAcademies() {
  return useQuery({
    queryKey: ["platform-academies"],
    queryFn: () => api.getPlatformAcademies().then((r) => r.data),
  });
}

export function usePlatformAcademy(id: string) {
  return useQuery({
    queryKey: ["platform-academy", id],
    queryFn: () => api.getPlatformAcademy(id).then((r) => r.data),
    enabled: !!id,
  });
}

export function usePlatformRevenue() {
  return useQuery({
    queryKey: ["platform-revenue"],
    queryFn: () => api.getPlatformRevenue().then((r) => r.data),
  });
}

export function usePlatformUsers() {
  return useQuery({
    queryKey: ["platform-users"],
    queryFn: () => api.getPlatformUsers().then((r) => r.data),
  });
}

export function usePlatformHealth() {
  return useQuery({
    queryKey: ["platform-health"],
    queryFn: () => api.getPlatformHealth().then((r) => r.data),
    refetchInterval: 30000,
  });
}

export function usePatchPlatformUser() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ userId, data }: { userId: string; data: { is_active: boolean } }) =>
      api.patchPlatformUser(userId, data).then((r) => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["platform-users"] }),
  });
}
