class ApiClient {
    constructor(baseUrl = "/api") {
        this.baseUrl = baseUrl;
    }

    getToken() {
        return localStorage.getItem("cn_auth_token");
    }

    setToken(token) {
        if (token) {
            localStorage.setItem("cn_auth_token", token);
        } else {
            localStorage.removeItem("cn_auth_token");
        }
    }

    async request(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        const headers = {
            ...options.headers,
        };

        const token = this.getToken();
        if (token) {
            headers["Authorization"] = `Bearer ${token}`;
        }

        if (!(options.body instanceof FormData) && !headers["Content-Type"]) {
            headers["Content-Type"] = "application/json";
        }

        try {
            const response = await fetch(url, {
                ...options,
                headers,
            });

            const data = await response.json().catch(() => ({}));

            if (!response.ok) {
                if (response.status === 401 && !endpoint.includes("/auth/")) {
                    this.setToken(null);
                    window.location.hash = "#/auth";
                }
                const errorMsg = data?.error?.message || `HTTP Error ${response.status}`;
                throw new Error(errorMsg);
            }

            return data;
        } catch (err) {
            throw err;
        }
    }

    get(endpoint, params = {}) {
        const qs = new URLSearchParams(params).toString();
        const url = qs ? `${endpoint}?${qs}` : endpoint;
        return this.request(url, { method: "GET" });
    }

    post(endpoint, body = {}) {
        return this.request(endpoint, {
            method: "POST",
            body: body instanceof FormData ? body : JSON.stringify(body),
        });
    }

    put(endpoint, body = {}) {
        return this.request(endpoint, {
            method: "PUT",
            body: JSON.stringify(body),
        });
    }

    delete(endpoint) {
        return this.request(endpoint, { method: "DELETE" });
    }

    // Authentication
    login(credentials) {
        return this.post("/auth/login", credentials);
    }

    register(userData) {
        return this.post("/auth/register", userData);
    }

    getCurrentUser() {
        return this.get("/auth/me");
    }

    // Projects
    getProjects() {
        return this.get("/projects");
    }

    createProject(projectData) {
        return this.post("/projects", projectData);
    }

    getProject(projectId) {
        return this.get(`/projects/${projectId}`);
    }

    uploadArchive(projectId, formData) {
        return this.post(`/projects/${projectId}/upload`, formData);
    }

    scanProject(projectId) {
        return this.post(`/projects/${projectId}/scan`);
    }

    deleteProject(projectId) {
        return this.delete(`/projects/${projectId}`);
    }

    // Tree & Files
    getProjectTree(projectId) {
        return this.get(`/projects/${projectId}/tree`);
    }

    getFileContent(projectId, filePath) {
        return this.get(`/projects/${projectId}/tree/file`, { path: filePath });
    }

    getFileIntelligence(projectId, filePath) {
        return this.get(`/projects/${projectId}/files/intelligence`, { path: filePath });
    }

    // Dependencies & Architecture
    getDependencies(projectId) {
        return this.get(`/projects/${projectId}/dependencies`);
    }

    getCircularDependencies(projectId) {
        return this.get(`/projects/${projectId}/dependencies/cycles`);
    }

    getArchitecture(projectId) {
        return this.get(`/projects/${projectId}/architecture`);
    }

    getArchitectureViolations(projectId) {
        return this.get(`/projects/${projectId}/architecture/violations`);
    }

    // Flows & Impact
    getCodeFlows(projectId) {
        return this.get(`/projects/${projectId}/flows`);
    }

    getFlowDetails(projectId, flowId) {
        return this.get(`/projects/${projectId}/flows/${flowId}`);
    }

    simulateImpact(projectId, payload) {
        return this.post(`/projects/${projectId}/impact/simulate`, payload);
    }

    getHighRiskModules(projectId) {
        return this.get(`/projects/${projectId}/impact/high-risk`);
    }

    // Search & Health
    search(projectId, params) {
        return this.get(`/projects/${projectId}/search`, params);
    }

    getHealthMetrics(projectId) {
        return this.get(`/projects/${projectId}/health`);
    }

    getHealthHotspots(projectId) {
        return this.get(`/projects/${projectId}/health/hotspots`);
    }

    // Onboarding & Knowledge Map
    getOnboardingPlan(projectId) {
        return this.get(`/projects/${projectId}/onboarding`);
    }

    submitQuiz(projectId, answers) {
        return this.post(`/projects/${projectId}/onboarding/quiz/submit`, { answers });
    }

    getKnowledgeMap(projectId) {
        return this.get(`/projects/${projectId}/knowledge-map`);
    }

    // AI Copilot
    queryCopilot(projectId, payload) {
        return this.post(`/projects/${projectId}/copilot/query`, payload);
    }

    getCopilotConversations(projectId) {
        return this.get(`/projects/${projectId}/copilot/conversations`);
    }

    getCopilotMessages(projectId, conversationId) {
        return this.get(`/projects/${projectId}/copilot/conversations/${conversationId}`);
    }

    // Reports & History
    getReport(projectId, format = "markdown") {
        return this.get(`/projects/${projectId}/reports/generate`, { format });
    }

    getAnalysisHistory(projectId) {
        return this.get(`/projects/${projectId}/history`);
    }

    // Settings
    getSettings() {
        return this.get("/settings");
    }

    updateAISettings(settings) {
        return this.post("/settings/ai", settings);
    }
}

export const api = new ApiClient();
