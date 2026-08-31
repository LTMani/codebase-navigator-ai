import { api } from "../api.js";
import { ToastManager } from "../components/toast.js";
import { store } from "../store.js";

export class HealthView {
    async render(container) {
        const activeProj = store.getState().activeProject;
        if (!activeProj) {
            container.innerHTML = `<div class="card text-center">Please select a project first.</div>`;
            return;
        }

        container.innerHTML = `
            <div class="flex items-center justify-center h-full text-secondary">
                Auditing codebase health and calculating metrics...
            </div>
        `;

        try {
            const res = await api.getHealthMetrics(activeProj.id);
            this.renderHealth(container, res.data);
        } catch (err) {
            ToastManager.error("Failed to load health metrics.");
        }
    }

    renderHealth(container, health) {
        const grade = health.maintainability_grade || "A";
        const score = health.overall_health_score || 100;
        const debtHours = health.estimated_technical_debt_hours || 0;
        const hotspots = health.hotspots || [];
        const recommendations = health.recommendations || [];

        container.innerHTML = `
            <div class="flex flex-col gap-6">
                <div>
                    <h2 style="font-size: 20px; font-weight: 700; margin-bottom: 4px;">Codebase Health & Technical Debt</h2>
                    <p class="text-secondary text-xs">Maintainability index, cyclomatic complexity distributions, and remediation debt.</p>
                </div>

                <!-- Top Dial and Debt Card -->
                <div class="card flex items-center justify-between" style="padding: 24px 32px;">
                    <div class="flex items-center gap-6">
                        <div class="health-score-dial grade-${grade.toLowerCase()}">
                            <div style="font-size: 32px; font-weight: 800;">${grade}</div>
                            <div class="text-xs text-muted font-bold">${score} / 100</div>
                        </div>
                        <div class="flex flex-col gap-1">
                            <h3 style="font-size: 18px; font-weight: 700;">Overall Maintainability Grade: ${grade}</h3>
                            <p class="text-secondary text-xs" style="max-width: 440px;">
                                Based on Halstead Software Science, McCabe Cyclomatic Complexity, line count, and circular coupling.
                            </p>
                        </div>
                    </div>

                    <div class="flex flex-col items-end gap-1">
                        <div class="text-xs text-muted font-bold uppercase">Estimated Technical Debt</div>
                        <div style="font-size: 28px; font-weight: 800; color: var(--accent-amber);">${debtHours} Hours</div>
                        <span class="text-xs text-secondary">To remediate high-risk code smells</span>
                    </div>
                </div>

                <!-- Metric Details Grid -->
                <div class="dashboard-metrics-grid">
                    <div class="metric-card">
                        <div>
                            <div class="metric-value">${health.average_cyclomatic_complexity}</div>
                            <div class="metric-label">Avg Cyclomatic Complexity</div>
                        </div>
                    </div>
                    <div class="metric-card">
                        <div>
                            <div class="metric-value">${health.average_maintainability_index} / 100</div>
                            <div class="metric-label">Avg Maintainability Index</div>
                        </div>
                    </div>
                    <div class="metric-card">
                        <div>
                            <div class="metric-value">${health.documentation_coverage_percent}%</div>
                            <div class="metric-label">Doc Comment Coverage</div>
                        </div>
                    </div>
                    <div class="metric-card">
                        <div>
                            <div class="metric-value">${health.circular_dependency_cycles_count}</div>
                            <div class="metric-label">Circular Cycles Detected</div>
                        </div>
                    </div>
                </div>

                <!-- Actionable Recommendations & Hotspots -->
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                    <!-- Recommendations -->
                    <div class="card flex flex-col gap-4">
                        <h3 style="font-size: 15px; font-weight: 600;">Actionable Recommendations</h3>
                        ${recommendations.map(r => `
                            <div class="card flex flex-col gap-1" style="background: var(--bg-tertiary); padding: 14px;">
                                <div class="flex items-center justify-between">
                                    <span style="font-weight: 700; font-size: 13px;">${r.title}</span>
                                    <span class="badge ${r.priority === 'High' ? 'badge-layer-presentation' : 'badge-layer-service'}">${r.priority}</span>
                                </div>
                                <p class="text-xs text-secondary" style="margin-top: 4px;">${r.detail}</p>
                            </div>
                        `).join("")}
                    </div>

                    <!-- Hotspots -->
                    <div class="card flex flex-col gap-4">
                        <h3 style="font-size: 15px; font-weight: 600;">Complexity Hotspots (${hotspots.length})</h3>
                        <div class="flex flex-col gap-2">
                            ${hotspots.slice(0, 6).map(h => `
                                <div class="flex items-center justify-between font-mono text-xs" style="padding: 10px 12px; background: var(--bg-tertiary); border-radius: var(--radius-sm);">
                                    <div class="flex flex-col truncate">
                                        <span style="font-weight: 700;">${h.filename}</span>
                                        <span class="text-muted text-xs truncate">${h.reasons.join(", ")}</span>
                                    </div>
                                    <span class="badge badge-layer-presentation">${h.hotspot_score} pts</span>
                                </div>
                            `).join("")}
                        </div>
                    </div>
                </div>
            </div>
        `;
    }
}
