import { api } from "../api.js";
import { ToastManager } from "../components/toast.js";
import { store } from "../store.js";

export class CircularDependenciesView {
    async render(container) {
        const activeProj = store.getState().activeProject;
        if (!activeProj) {
            container.innerHTML = `<div class="card text-center">Please select a project first.</div>`;
            return;
        }

        container.innerHTML = `
            <div class="flex items-center justify-center h-full text-secondary">
                Analyzing circular dependency cycles...
            </div>
        `;

        try {
            const res = await api.getCircularDependencies(activeProj.id);
            this.renderCycles(container, res.data);
        } catch (err) {
            ToastManager.error("Failed to load circular dependencies.");
        }
    }

    renderCycles(container, data) {
        const cycles = data.cycles || [];

        container.innerHTML = `
            <div class="flex flex-col gap-6">
                <div>
                    <h2 style="font-size: 20px; font-weight: 700; margin-bottom: 4px;">Circular Dependency Loops</h2>
                    <p class="text-secondary text-xs">
                        Mutual imports and dependency cycles detected using Tarjan's Strongly Connected Components algorithm.
                    </p>
                </div>

                <div class="card flex items-center justify-between">
                    <div>
                        <div class="text-xs text-muted font-bold uppercase">Circular Cycles Found</div>
                        <div style="font-size: 28px; font-weight: 800; color: ${cycles.length > 0 ? 'var(--accent-rose)' : 'var(--accent-emerald)'};">
                            ${cycles.length} Loops
                        </div>
                    </div>
                    <span class="badge ${cycles.length === 0 ? 'badge-layer-domain' : 'badge-layer-presentation'}">
                        ${cycles.length === 0 ? 'CLEAN ARCHITECTURE' : 'COUPLING WARNING'}
                    </span>
                </div>

                ${cycles.length > 0 ? `
                    <div class="flex flex-col gap-4">
                        ${cycles.map((c, i) => `
                            <div class="card flex flex-col gap-3" style="border-left: 4px solid var(--accent-rose);">
                                <div class="flex items-center justify-between">
                                    <span style="font-weight: 700; font-size: 14px;">Loop #${i + 1} (${c.length} Files)</span>
                                    <span class="badge badge-layer-presentation">Critical Coupling</span>
                                </div>
                                <div class="font-mono text-xs text-accent" style="padding: 10px; background: var(--bg-tertiary); border-radius: var(--radius-sm); word-break: break-all;">
                                    ${c.join(" &rarr; ")} &rarr; <strong>${c[0]}</strong>
                                </div>
                                <p class="text-xs text-secondary">
                                    💡 <strong>Refactoring Tip</strong>: Break this loop by introducing a shared abstraction or dependency inversion interface between <code>${c[0]}</code> and <code>${c[1]}</code>.
                                </p>
                            </div>
                        `).join("")}
                    </div>
                ` : `
                    <div class="card text-center text-secondary" style="padding: 48px 0;">
                        <div style="font-size: 32px; margin-bottom: 8px;">✅</div>
                        <h3 style="font-size: 16px; font-weight: 600;">No Circular Dependency Loops Detected</h3>
                        <p class="text-xs text-muted">The codebase maintains a healthy Directed Acyclic Graph (DAG) structure.</p>
                    </div>
                `}
            </div>
        `;
    }
}
