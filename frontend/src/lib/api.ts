import axios, { AxiosInstance, InternalAxiosRequestConfig } from "axios";

const API_BASE = (process.env.NEXT_PUBLIC_API_URL || "") + "/api/v1";

class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE,
      headers: { "Content-Type": "application/json" },
    });

    // attach the token and org id to every outgoing request
    this.client.interceptors.request.use((config: InternalAxiosRequestConfig) => {
      if (typeof window !== "undefined") {
        const token = localStorage.getItem("access_token");
        const orgId = localStorage.getItem("current_org_id");
        if (token) config.headers.Authorization = `Bearer ${token}`;
        if (orgId) config.headers["X-Organization-Id"] = orgId;
      }
      return config;
    });

    // if we get a 401, try using the refresh token before giving up
    this.client.interceptors.response.use(
      (r) => r,
      async (error) => {
        if (error.response?.status === 401 && typeof window !== "undefined") {
          const refresh = localStorage.getItem("refresh_token");
          if (refresh) {
            try {
              const { data } = await axios.post(`${API_BASE}/auth/refresh`, {
                refresh_token: refresh,
              });
              localStorage.setItem("access_token", data.access_token);
              localStorage.setItem("refresh_token", data.refresh_token);
              error.config.headers.Authorization = `Bearer ${data.access_token}`;
              return this.client.request(error.config);
            } catch {
              localStorage.clear();
              window.location.href = "/login";
            }
          }
        }
        return Promise.reject(error);
      }
    );
  }

  login(email: string, password: string) {
    return this.client.post("/auth/login", { email, password });
  }

  register(email: string, password: string, fullName: string) {
    return this.client.post("/auth/register", {
      email,
      password,
      full_name: fullName,
    });
  }

  getMe() {
    return this.client.get("/auth/me");
  }

  getOrganizations() {
    return this.client.get("/orgs");
  }

  getEvents(params?: Record<string, string>) {
    return this.client.get("/events", { params });
  }

  getEvent(id: string) {
    return this.client.get(`/events/${id}`);
  }

  createEvent(data: Record<string, unknown>) {
    return this.client.post("/events", data);
  }

  getBookings(params?: Record<string, string>) {
    return this.client.get("/bookings", { params });
  }

  getOverviewKPIs(days = 30) {
    return this.client.get("/analytics/overview", { params: { days } });
  }

  getRevenueByDay(days = 30) {
    return this.client.get("/analytics/revenue", { params: { days } });
  }

  getCohorts(months = 6) {
    return this.client.get("/analytics/cohorts", { params: { months } });
  }

  getLTVDistribution() {
    return this.client.get("/analytics/ltv-distribution");
  }

  getNoShowRisks(limit = 20) {
    return this.client.get("/analytics/no-show-risk", { params: { limit } });
  }

  getEventPerformance() {
    return this.client.get("/events/performance");
  }

  getPricingRecommendations(eventId?: string) {
    return this.client.get("/pricing/recommendations", {
      params: eventId ? { event_id: eventId } : {},
    });
  }

  generateRecommendation(eventId: string) {
    return this.client.post(`/pricing/recommendations/${eventId}/generate`);
  }

  whatIfSimulate(eventId: string, pricePoints: number[]) {
    return this.client.post("/pricing/what-if", {
      event_id: eventId,
      price_points: pricePoints,
    });
  }

  getChangeRequests(status?: string) {
    return this.client.get("/pricing/change-requests", {
      params: status ? { status } : {},
    });
  }

  createChangeRequest(data: {
    event_id: string;
    new_price: number;
    reason?: string;
    recommendation_id?: string;
  }) {
    return this.client.post("/pricing/change-requests", data);
  }

  approveChangeRequest(requestId: string) {
    return this.client.post(`/pricing/change-requests/${requestId}/approve`);
  }

  getExperiments() {
    return this.client.get("/experiments");
  }

  createExperiment(data: Record<string, unknown>) {
    return this.client.post("/experiments", data);
  }

  getAuditLogs(page = 1) {
    return this.client.get("/admin/audit-logs", { params: { page } });
  }

  getFeatureFlags() {
    return this.client.get("/admin/feature-flags");
  }

  toggleFeatureFlag(flagId: string, enabled: boolean) {
    return this.client.patch(`/admin/feature-flags/${flagId}`, null, {
      params: { enabled },
    });
  }

  getInsights() {
    return this.client.get("/admin/insights");
  }

  generateInsight() {
    return this.client.post("/admin/insights/generate");
  }

  getCoaches() {
    return this.client.get("/coaches");
  }

  importEvents(file: File) {
    const form = new FormData();
    form.append("file", file);
    return this.client.post("/imports/events", form, {
      headers: { "Content-Type": "multipart/form-data" },
    });
  }

  importBookings(file: File) {
    const form = new FormData();
    form.append("file", file);
    return this.client.post("/imports/bookings", form, {
      headers: { "Content-Type": "multipart/form-data" },
    });
  }

  exportEvents() {
    return this.client.get("/exports/events", { responseType: "blob" });
  }

  exportCohorts() {
    return this.client.get("/exports/cohorts", { responseType: "blob" });
  }

  // platform (superadmin) endpoints
  getPlatformOverview() { return this.client.get("/platform/overview"); }
  getPlatformAcademies() { return this.client.get("/platform/academies"); }
  getPlatformAcademy(orgId: string) { return this.client.get(`/platform/academies/${orgId}`); }
  getPlatformRevenue() { return this.client.get("/platform/revenue"); }
  getPlatformUsers() { return this.client.get("/platform/users"); }
  patchPlatformUser(userId: string, data: { is_active: boolean }) { return this.client.patch(`/platform/users/${userId}`, data); }
  getPlatformHealth() { return this.client.get("/platform/health"); }
  createAcademy(data: Record<string, unknown>) { return this.client.post("/platform/academies", data); }

  // evaluation endpoints
  getEvaluations(params?: { status?: string; athlete_id?: string }) { return this.client.get("/evaluations", { params }); }
  getEvaluationStats() { return this.client.get("/evaluations/stats"); }
  getEvaluationTemplates() { return this.client.get("/evaluations/templates"); }
  getAthleteEvaluations(athleteId: string) { return this.client.get(`/evaluations/athlete/${athleteId}`); }
  getEvaluation(evalId: string) { return this.client.get(`/evaluations/${evalId}`); }
  createEvaluation(data: Record<string, unknown>) { return this.client.post("/evaluations", data); }
  updateEvaluation(evalId: string, data: Record<string, unknown>) { return this.client.patch(`/evaluations/${evalId}`, data); }
  generateEvaluationNarrative(evalId: string) { return this.client.post(`/evaluations/${evalId}/generate-narrative`); }
  publishEvaluation(evalId: string) { return this.client.post(`/evaluations/${evalId}/publish`); }
}

export const api = new ApiClient();
