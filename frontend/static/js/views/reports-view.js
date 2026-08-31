import { api } from "../api.js";
import { ToastManager } from "../components/toast.js";
import { store } from "../store.js";

export class ReportsView {
    async render(container) {
        const activeProj = store.getState().activeProject;
        if (!activeProj) {
            container.innerHTML = `<div class="card text-center">Please select a project first.</div>`;
            return;
        }

        container.innerHTML = `
            <div class="flex flex-col gap-6">
                <div>
                    <h2 style="font-size: 20px; font-weight: 700; margin-bottom: 4px;">Architecture & Health Audit Reports</h2>
                    <p class="text-secondary text-xs">Export standardized architecture audit reports in Markdown and JSON formats.</p>
                </div>

                <div class="card flex items-center justify-between">
                    <div class="flex items-center gap-3">
                        <span style="font-size: 24px;">📄</span>
                        <div>
                            <h3 style="font-size: 15px; font-weight: 700;">Full Codebase Architecture Report</h3>
                            <span class="text-xs text-muted">Includes metrics, 6-layer breakdown, Tarjan cycles, and onboarding paths.</span>
                        </div>
                    </div>
                    <div class="flex items-center gap-3">
                        <button id="btn-view-report-md" class="btn btn-secondary btn-sm">Preview Markdown</button>
                        <a id="btn-download-report-md" href="/api/projects/${activeProj.id}/reports/generate?format=markdown&download=true" class="btn btn-primary btn-sm" target="_blank">📥 Download (.md)</a>
                    </div>
                </div>

                <div id="report-preview-target" class="card" style="display: none; background: var(--bg-tertiary);">
                    <div class="flex items-center justify-between" style="border-bottom: 1px solid var(--border-color); padding-bottom: 12px; margin-bottom: 16px;">
                        <span class="font-mono text-xs font-bold">REPORT PREVIEW</span>
                        <button id="btn-close-preview" class="btn btn-outline btn-sm">Close</button>
                    </div>
                    <pre id="report-text-content" class="font-mono text-xs" style="white-space: pre-wrap; line-height: 1.6; max-height: 500px; overflow-y: auto; color: var(--text-primary);"></pre>
                </div>
            </div>
        `;

        const viewBtn = container.querySelector("#btn-view-report-md");
        const previewTarget = container.querySelector("#report-preview-target");
        const textTarget = container.querySelector("#report-text-content");
        const closeBtn = container.querySelector("#btn-close-preview");

        viewBtn.addEventListener("click", async () => {
            try {
                viewBtn.disabled = true;
                const res = await api.getReport(activeProj.id, "markdown");
                textTarget.textContent = res.data.content;
                previewTarget.style.display = "block";
            } catch (err) {
                ToastManager.error("Failed to generate report.");
            } finally {
                viewBtn.disabled = false;
            }
        });

        closeBtn.addEventListener("click", () => {
            previewTarget.style.display = "none";
        });
    }
}
