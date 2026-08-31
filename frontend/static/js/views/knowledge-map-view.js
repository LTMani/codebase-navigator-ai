import { api } from "../api.js";
import { ToastManager } from "../components/toast.js";
import { store } from "../store.js";

export class KnowledgeMapView {
    async render(container) {
        const activeProj = store.getState().activeProject;
        if (!activeProj) {
            container.innerHTML = `<div class="card text-center">Please select a project first.</div>`;
            return;
        }

        container.innerHTML = `
            <div class="flex items-center justify-center h-full text-secondary">
                Generating conceptual knowledge map...
            </div>
        `;

        try {
            const res = await api.getKnowledgeMap(activeProj.id);
            this.renderMap(container, res.data);
        } catch (err) {
            ToastManager.error("Failed to load knowledge map.");
        }
    }

    renderMap(container, data) {
        const clusters = data.domain_clusters || [];
        const concepts = data.key_concepts || [];

        container.innerHTML = `
            <div class="flex flex-col gap-6">
                <div>
                    <h2 style="font-size: 20px; font-weight: 700; margin-bottom: 4px;">Codebase Conceptual Knowledge Map</h2>
                    <p class="text-secondary text-xs">High-level domain clusters, key abstractions, and cross-module relationships.</p>
                </div>

                <!-- Domain Clusters Grid -->
                <div class="card flex flex-col gap-4">
                    <h3 style="font-size: 15px; font-weight: 600;">Domain Clusters (${clusters.length})</h3>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 16px;">
                        ${clusters.map(c => `
                            <div class="card flex flex-col gap-2" style="background: var(--bg-tertiary); border-left: 4px solid var(--layer-${c.layer});">
                                <div class="flex items-center justify-between">
                                    <h4 style="font-size: 15px; font-weight: 700;">${c.name}</h4>
                                    <span class="badge badge-layer-${c.layer}">${c.layer}</span>
                                </div>
                                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 4px; font-size: 11px;" class="text-secondary">
                                    <div>Files: <span class="text-primary font-bold">${c.file_count}</span></div>
                                    <div>Lines: <span class="text-primary font-bold">${c.total_lines}</span></div>
                                </div>
                                ${c.key_abstractions?.length ? `
                                    <div class="flex flex-wrap gap-1" style="margin-top: 6px;">
                                        ${c.key_abstractions.map(a => `<span class="badge" style="background: rgba(255,255,255,0.05); font-size: 10px;">${a}</span>`).join("")}
                                    </div>
                                ` : ''}
                            </div>
                        `).join("")}
                    </div>
                </div>

                <!-- Key Abstractions & Hubs -->
                <div class="card flex flex-col gap-4">
                    <h3 style="font-size: 15px; font-weight: 600;">Core Abstraction Nodes (${concepts.length})</h3>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 12px;">
                        ${concepts.map(c => `
                            <div class="flex items-center justify-between font-mono text-xs" style="padding: 10px 12px; background: var(--bg-tertiary); border-radius: var(--radius-sm);">
                                <div class="flex items-center gap-2">
                                    <span style="color: var(--accent-amber);">🔷</span>
                                    <span style="font-weight: 700;">${c.name}</span>
                                </div>
                                <span class="badge badge-layer-${c.layer}">${c.layer}</span>
                            </div>
                        `).join("")}
                    </div>
                </div>
            </div>
        `;
    }
}
