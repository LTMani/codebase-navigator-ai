export class DiffViewerComponent {
    static renderImpactSummary(container, impactResult) {
        if (!container || !impactResult) return;

        const {
            blast_radius_score = 0,
            risk_level = "low",
            direct_dependents = [],
            indirect_dependents = [],
            affected_routes = [],
            affected_tests = [],
        } = impactResult;

        const riskColors = {
            low: "var(--accent-emerald)",
            medium: "var(--accent-amber)",
            high: "var(--accent-rose)",
            critical: "#ef4444",
        };

        container.innerHTML = `
            <div class="flex flex-col gap-4">
                <div class="card flex items-center justify-between" style="border-left: 4px solid ${riskColors[risk_level] || 'var(--accent-primary)'};">
                    <div>
                        <div class="text-xs text-muted font-bold uppercase">Blast Radius Score</div>
                        <div style="font-size: 28px; font-weight: 800; color: ${riskColors[risk_level]};">${blast_radius_score} / 100</div>
                    </div>
                    <div class="badge" style="font-size: 13px; padding: 4px 12px; background: rgba(255,255,255,0.05); color: ${riskColors[risk_level]};">
                        ${risk_level.toUpperCase()} RISK
                    </div>
                </div>

                <div class="dashboard-metrics-grid" style="margin-bottom: 0;">
                    <div class="metric-card">
                        <div class="metric-value">${direct_dependents.length}</div>
                        <div class="metric-label">Direct Dependents</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">${indirect_dependents.length}</div>
                        <div class="metric-label">Transitive Dependents</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">${affected_routes.length}</div>
                        <div class="metric-label">Affected Endpoints</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">${affected_tests.length}</div>
                        <div class="metric-label">Affected Tests</div>
                    </div>
                </div>

                <div class="card flex flex-col gap-3">
                    <h4 style="font-size: 14px; font-weight: 600;">Directly Affected Files</h4>
                    ${direct_dependents.length > 0 ? `
                        <div class="flex flex-col gap-1">
                            ${direct_dependents.map(d => `
                                <div class="flex items-center gap-2 font-mono text-xs" style="padding: 4px 8px; background: var(--bg-tertiary); border-radius: var(--radius-sm);">
                                    <span>⚠️</span>
                                    <span>${d}</span>
                                </div>
                            `).join("")}
                        </div>
                    ` : '<div class="text-xs text-muted">No files directly import this module.</div>'}
                </div>
            </div>
        `;
    }
}
