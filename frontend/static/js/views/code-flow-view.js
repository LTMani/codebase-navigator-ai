import { api } from "../api.js";
import { ToastManager } from "../components/toast.js";
import { store } from "../store.js";

export class CodeFlowView {
    async render(container) {
        const activeProj = store.getState().activeProject;
        if (!activeProj) {
            container.innerHTML = `<div class="card text-center">Please select a project first.</div>`;
            return;
        }

        container.innerHTML = `
            <div class="flex flex-col gap-6">
                <div>
                    <h2 style="font-size: 20px; font-weight: 700; margin-bottom: 4px;">End-to-End Code Flow Explorer</h2>
                    <p class="text-secondary text-xs">
                        Synthesized request-to-persistence execution paths across routes, services, and repositories.
                    </p>
                </div>

                <div id="flows-list-container">
                    <div class="text-center text-secondary" style="padding: 32px 0;">Loading discovered flows...</div>
                </div>
            </div>
        `;

        const flowsContainer = container.querySelector("#flows-list-container");

        try {
            const res = await api.getCodeFlows(activeProj.id);
            const flows = res.data?.flows || [];
            this.renderFlows(flowsContainer, flows);
        } catch (err) {
            ToastManager.error("Failed to load code flows.");
        }
    }

    renderFlows(container, flows) {
        if (!flows || flows.length === 0) {
            container.innerHTML = `
                <div class="card text-center" style="padding: 48px;">
                    <div style="font-size: 32px; margin-bottom: 8px;">⚡</div>
                    <h3 style="font-size: 16px; font-weight: 600;">No Multi-Layer Flows Discovered</h3>
                    <p class="text-secondary text-xs">Could not find route handler entry points calling services.</p>
                </div>
            `;
            return;
        }

        container.innerHTML = `
            <div class="flex flex-col gap-6">
                ${flows.map(f => {
                    const steps = f.steps || [];
                    return `
                        <div class="card flex flex-col gap-4">
                            <div class="flex items-center justify-between border-b" style="border-bottom: 1px solid var(--border-color); padding-bottom: 12px;">
                                <div class="flex items-center gap-3">
                                    <span style="font-size: 20px;">⚡</span>
                                    <div>
                                        <h3 style="font-size: 16px; font-weight: 700;">${f.flow_name}</h3>
                                        <span class="font-mono text-xs text-muted">Entry: ${f.entry_point}</span>
                                    </div>
                                </div>
                                <span class="badge badge-layer-service">${f.step_count} Steps</span>
                            </div>

                            <p class="text-xs text-secondary">${f.description}</p>

                            <!-- Sequential Flow Timeline -->
                            <div class="timeline-list">
                                ${steps.map(s => `
                                    <div class="timeline-item">
                                        <div class="timeline-dot"></div>
                                        <div class="card flex flex-col gap-1" style="background: var(--bg-tertiary); padding: 12px;">
                                            <div class="flex items-center justify-between font-mono text-xs">
                                                <div class="flex items-center gap-2">
                                                    <span class="badge badge-layer-${s.layer_name}">${s.layer_name}</span>
                                                    <span style="font-weight: 600; color: var(--text-primary);">${s.symbol_name}()</span>
                                                </div>
                                                <span class="text-muted">${s.file_path}</span>
                                            </div>
                                            <div class="text-xs text-secondary" style="margin-top: 4px;">${s.action}</div>
                                        </div>
                                    </div>
                                `).join("")}
                            </div>
                        </div>
                    `;
                }).join("")}
            </div>
        `;
    }
}
