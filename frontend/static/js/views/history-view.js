import { api } from "../api.js";
import { ToastManager } from "../components/toast.js";
import { store } from "../store.js";

export class HistoryView {
    async render(container) {
        const activeProj = store.getState().activeProject;
        if (!activeProj) {
            container.innerHTML = `<div class="card text-center">Please select a project first.</div>`;
            return;
        }

        container.innerHTML = `
            <div class="flex items-center justify-center h-full text-secondary">
                Loading analysis history...
            </div>
        `;

        try {
            const res = await api.getAnalysisHistory(activeProj.id);
            this.renderHistory(container, res.data.history || [], activeProj);
        } catch (err) {
            ToastManager.error("Failed to load history.");
        }
    }

    renderHistory(container, history, project) {
        container.innerHTML = `
            <div class="flex flex-col gap-6">
                <div class="flex items-center justify-between">
                    <div>
                        <h2 style="font-size: 20px; font-weight: 700; margin-bottom: 4px;">Analysis Runs History</h2>
                        <p class="text-secondary text-xs">Chronological timeline of code indexing and structural analysis scans.</p>
                    </div>
                    <button id="btn-trigger-scan-now" class="btn btn-primary btn-sm">⚡ Run New Analysis</button>
                </div>

                ${history.length > 0 ? `
                    <div class="timeline-list">
                        ${history.map(h => `
                            <div class="timeline-item">
                                <div class="timeline-dot"></div>
                                <div class="card flex items-center justify-between" style="background: var(--bg-tertiary); padding: 16px;">
                                    <div class="flex flex-col gap-1">
                                        <div class="flex items-center gap-3">
                                            <span style="font-weight: 700; font-size: 14px;">Analysis Run #${h.run_number || 1}</span>
                                            <span class="badge ${h.status === 'completed' ? 'badge-layer-domain' : 'badge-layer-presentation'}">${h.status}</span>
                                        </div>
                                        <div class="text-xs text-muted font-mono">Completed: ${new Date(h.created_at).toLocaleString()}</div>
                                    </div>
                                    <div class="flex items-center gap-6 font-mono text-xs">
                                        <div>Files: <span class="text-primary font-bold">${h.total_files}</span></div>
                                        <div>Lines: <span class="text-primary font-bold">${h.total_lines?.toLocaleString() || 0}</span></div>
                                        <div>Time: <span class="text-accent font-bold">${h.duration_ms} ms</span></div>
                                    </div>
                                </div>
                            </div>
                        `).join("")}
                    </div>
                ` : '<div class="card text-center text-secondary" style="padding: 48px 0;">No analysis runs recorded yet.</div>'}
            </div>
        `;

        container.querySelector("#btn-trigger-scan-now")?.addEventListener("click", async () => {
            try {
                ToastManager.info("Starting fresh AST scan...");
                await api.scanProject(project.id);
                ToastManager.success("Analysis complete!");
                this.render(container);
            } catch (err) {
                ToastManager.error("Scan failed.");
            }
        });
    }
}
