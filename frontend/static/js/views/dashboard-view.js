import { api } from "../api.js";
import { MetricsChartComponent } from "../components/metrics-chart.js";
import { ToastManager } from "../components/toast.js";
import { store } from "../store.js";

export class DashboardView {
    async render(container) {
        container.innerHTML = `
            <div class="flex items-center justify-center h-full">
                <div class="text-secondary">Loading dashboard metrics...</div>
            </div>
        `;

        try {
            const projectsRes = await api.getProjects();
            const projects = projectsRes.data?.projects || [];
            store.setProjects(projects);

            const activeProj = store.getState().activeProject || projects[0];

            let healthData = null;
            if (activeProj) {
                try {
                    const hRes = await api.getHealthMetrics(activeProj.id);
                    healthData = hRes.data;
                } catch (e) {
                    console.warn("Could not load health metrics for active project", e);
                }
            }

            this.renderDashboard(container, projects, activeProj, healthData);
        } catch (err) {
            container.innerHTML = `
                <div class="card text-center" style="padding: 48px;">
                    <div style="font-size: 32px; margin-bottom: 12px;">📂</div>
                    <h3 style="font-size: 18px; font-weight: 600; margin-bottom: 8px;">No Codebases Imported Yet</h3>
                    <p class="text-secondary text-sm" style="max-width: 480px; margin: 0 auto 20px;">
                        Upload a ZIP / TAR archive or provide a repository URL to extract code intelligence and start navigating.
                    </p>
                    <a href="#/import" class="btn btn-primary">Import First Project</a>
                </div>
            `;
        }
    }

    renderDashboard(container, projects, activeProj, healthData) {
        if (!activeProj) {
            container.innerHTML = `
                <div class="card text-center" style="padding: 48px;">
                    <h3 style="font-size: 18px; font-weight: 600; margin-bottom: 8px;">No Active Project Selected</h3>
                    <a href="#/import" class="btn btn-primary">Import New Project</a>
                </div>
            `;
            return;
        }

        const grade = healthData?.maintainability_grade || "A";

        container.innerHTML = `
            <div class="flex flex-col gap-6">
                <!-- Welcome Banner -->
                <div class="card flex items-center justify-between" style="background: linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.9) 100%);">
                    <div class="flex flex-col gap-1">
                        <div class="flex items-center gap-3">
                            <h2 style="font-size: 22px; font-weight: 700;">${activeProj.name}</h2>
                            <span class="badge badge-layer-service">${activeProj.version}</span>
                        </div>
                        <p class="text-secondary text-sm">
                            ${activeProj.description || "Parsed codebase repository ready for exploration."}
                        </p>
                    </div>
                    <div class="flex items-center gap-3">
                        <a href="#/workspace" class="btn btn-primary">
                            <span>💻</span>
                            <span>Open Workspace</span>
                        </a>
                        <a href="#/onboarding" class="btn btn-secondary">
                            <span>🧭</span>
                            <span>Onboarding Tour</span>
                        </a>
                    </div>
                </div>

                <!-- High-level Metric Cards Grid -->
                <div class="dashboard-metrics-grid">
                    <div class="metric-card">
                        <div>
                            <div class="metric-value">${activeProj.file_count}</div>
                            <div class="metric-label">Source Files</div>
                        </div>
                        <span style="font-size: 24px;">📁</span>
                    </div>

                    <div class="metric-card">
                        <div>
                            <div class="metric-value">${(activeProj.total_lines || 0).toLocaleString()}</div>
                            <div class="metric-label">Total Lines</div>
                        </div>
                        <span style="font-size: 24px;">📝</span>
                    </div>

                    <div class="metric-card">
                        <div>
                            <div class="metric-value">${healthData?.overall_health_score || 100} / 100</div>
                            <div class="metric-label">Health Score (Grade ${grade})</div>
                        </div>
                        <span style="font-size: 24px;">🩺</span>
                    </div>

                    <div class="metric-card">
                        <div>
                            <div class="metric-value">${healthData?.estimated_technical_debt_hours || 0} hrs</div>
                            <div class="metric-label">Technical Debt</div>
                        </div>
                        <span style="font-size: 24px;">⏱️</span>
                    </div>
                </div>

                <!-- 2-Column Overview Panels -->
                <div style="display: grid; grid-template-columns: 2fr 1fr; gap: 20px;">
                    <!-- Left: Language Distribution & Navigation Hub -->
                    <div class="card flex flex-col gap-4">
                        <h3 style="font-size: 15px; font-weight: 600;">Programming Languages & Tech Stack</h3>
                        <div id="dashboard-lang-chart"></div>

                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-top: 12px;">
                            <a href="#/architecture" class="layer-box flex items-center justify-between">
                                <div class="flex items-center gap-2">
                                    <span>🏗️</span>
                                    <span style="font-weight: 600; font-size: 13px;">Architecture Layers</span>
                                </div>
                                <span class="text-xs text-muted">6 Tiers &rarr;</span>
                            </a>

                            <a href="#/dependencies" class="layer-box flex items-center justify-between">
                                <div class="flex items-center gap-2">
                                    <span>🕸️</span>
                                    <span style="font-weight: 600; font-size: 13px;">Dependency Graph</span>
                                </div>
                                <span class="text-xs text-muted">Interactive &rarr;</span>
                            </a>

                            <a href="#/flows" class="layer-box flex items-center justify-between">
                                <div class="flex items-center gap-2">
                                    <span>⚡</span>
                                    <span style="font-weight: 600; font-size: 13px;">Code Flows</span>
                                </div>
                                <span class="text-xs text-muted">Traces &rarr;</span>
                            </a>

                            <a href="#/impact" class="layer-box flex items-center justify-between">
                                <div class="flex items-center gap-2">
                                    <span>💥</span>
                                    <span style="font-weight: 600; font-size: 13px;">Impact Simulator</span>
                                </div>
                                <span class="text-xs text-muted">Blast Radius &rarr;</span>
                            </a>
                        </div>
                    </div>

                    <!-- Right: Quick Health Hotspots -->
                    <div class="card flex flex-col gap-3">
                        <div class="flex items-center justify-between">
                            <h3 style="font-size: 15px; font-weight: 600;">Complexity Hotspots</h3>
                            <a href="#/health" class="text-xs text-accent">View All &rarr;</a>
                        </div>

                        ${healthData?.hotspots?.length > 0 ? `
                            <div class="flex flex-col gap-2">
                                ${healthData.hotspots.slice(0, 4).map(h => `
                                    <div class="flex items-center justify-between font-mono text-xs" style="padding: 8px 10px; background: var(--bg-tertiary); border-radius: var(--radius-sm);">
                                        <div class="flex flex-col truncate">
                                            <span style="font-weight: 600;" class="truncate">${h.filename}</span>
                                            <span class="text-muted truncate">${h.reasons[0] || 'High complexity'}</span>
                                        </div>
                                        <span class="badge badge-layer-presentation" style="font-size: 10px;">${h.hotspot_score} pts</span>
                                    </div>
                                `).join("")}
                            </div>
                        ` : '<div class="text-xs text-muted" style="padding: 16px 0;">No severe hotspots detected! Codebase is well-structured.</div>'}
                    </div>
                </div>
            </div>
        `;

        const langContainer = container.querySelector("#dashboard-lang-chart");
        if (langContainer && activeProj.languages) {
            MetricsChartComponent.renderLanguageDistribution(langContainer, activeProj.languages);
        }
    }
}
