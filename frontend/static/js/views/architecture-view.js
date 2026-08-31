import { api } from "../api.js";
import { ToastManager } from "../components/toast.js";
import { store } from "../store.js";

export class ArchitectureView {
    async render(container) {
        const activeProj = store.getState().activeProject;
        if (!activeProj) {
            container.innerHTML = `<div class="card text-center">Please select a project first.</div>`;
            return;
        }

        container.innerHTML = `
            <div class="flex items-center justify-center h-full text-secondary">
                Analyzing architectural layers...
            </div>
        `;

        try {
            const res = await api.getArchitecture(activeProj.id);
            const arch = res.data;
            this.renderArchitecture(container, arch);
        } catch (err) {
            ToastManager.error("Failed to load architectural analysis.");
        }
    }

    renderArchitecture(container, arch) {
        const layers = arch.layers || [];
        const violations = arch.violations || [];

        container.innerHTML = `
            <div class="flex flex-col gap-6">
                <div>
                    <h2 style="font-size: 20px; font-weight: 700; margin-bottom: 4px;">Layered Architecture Classification</h2>
                    <p class="text-secondary text-xs">
                        6-tier architectural hierarchy, component boundaries, and structural rule violations.
                    </p>
                </div>

                <!-- Architectural Tier Stack -->
                <div class="card flex flex-col gap-4">
                    <h3 style="font-size: 15px; font-weight: 600;">Classified Architectural Stack</h3>
                    <div class="layer-stack-container">
                        ${layers.map(l => `
                            <div class="layer-box" style="border-left: 4px solid var(--layer-${l.layer_name});">
                                <div class="flex items-center gap-3">
                                    <span class="badge badge-layer-${l.layer_name}">${l.layer_name}</span>
                                    <div>
                                        <div style="font-weight: 600; font-size: 14px;">${l.component_name}</div>
                                        <div class="text-xs text-muted">${l.description}</div>
                                    </div>
                                </div>
                                <div class="flex items-center gap-4 text-xs font-mono">
                                    <div>Files: <span class="text-primary font-bold">${l.file_count}</span></div>
                                    <div>Confidence: <span class="text-accent font-bold">${(l.confidence_score * 100).toFixed(0)}%</span></div>
                                </div>
                            </div>
                        `).join("")}
                    </div>
                </div>

                <!-- Architectural Violations -->
                <div class="card flex flex-col gap-4">
                    <div class="flex items-center justify-between">
                        <h3 style="font-size: 15px; font-weight: 600;">Boundary Rule Violations</h3>
                        <span class="badge ${violations.length === 0 ? 'badge-layer-domain' : 'badge-layer-presentation'}">
                            ${violations.length} Detected
                        </span>
                    </div>

                    ${violations.length > 0 ? `
                        <div class="flex flex-col gap-2">
                            ${violations.map(v => `
                                <div class="card flex flex-col gap-1" style="background: rgba(244,63,94,0.05); border: 1px solid rgba(244,63,94,0.2); padding: 12px;">
                                    <div class="flex items-center justify-between">
                                        <span style="font-weight: 600; font-size: 13px; color: var(--accent-rose);">${v.rule_name}</span>
                                        <span class="badge" style="background: rgba(244,63,94,0.15); color: var(--accent-rose);">${v.severity}</span>
                                    </div>
                                    <div class="font-mono text-xs text-secondary">
                                        <code>${v.source_file_path}</code> &rarr; <code>${v.target_file_path}</code>
                                    </div>
                                    <p class="text-xs text-muted" style="margin-top: 4px;">${v.explanation}</p>
                                </div>
                            `).join("")}
                        </div>
                    ` : '<div class="text-xs text-muted" style="padding: 12px 0;">No architectural boundary violations detected. Clean separation of concerns!</div>'}
                </div>
            </div>
        `;
    }
}
