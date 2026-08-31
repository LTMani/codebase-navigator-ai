import { api } from "../api.js";
import { DiffViewerComponent } from "../components/diff-viewer.js";
import { ToastManager } from "../components/toast.js";
import { store } from "../store.js";

export class ImpactView {
    async render(container) {
        const activeProj = store.getState().activeProject;
        if (!activeProj) {
            container.innerHTML = `<div class="card text-center">Please select a project first.</div>`;
            return;
        }

        container.innerHTML = `
            <div class="flex flex-col gap-6">
                <div>
                    <h2 style="font-size: 20px; font-weight: 700; margin-bottom: 4px;">Change Blast Radius Simulator</h2>
                    <p class="text-secondary text-xs">
                        Simulate breaking changes and calculate downstream dependency risk before refactoring.
                    </p>
                </div>

                <div class="card flex flex-col gap-4">
                    <h3 style="font-size: 14px; font-weight: 600;">Simulate File or Symbol Modification</h3>
                    <div class="flex items-center gap-3">
                        <input type="text" id="impact-target-input" class="input-field font-mono text-xs" placeholder="e.g. models/user.py or services/auth_service.py..." />
                        <button id="btn-run-simulation" class="btn btn-primary btn-sm flex-shrink-0">
                            <span>💥</span>
                            <span>Calculate Blast Radius</span>
                        </button>
                    </div>
                </div>

                <div id="impact-results-target">
                    <div class="text-center text-secondary" style="padding: 48px 0;">
                        Enter a target file above to calculate affected files, routes, and test suites.
                    </div>
                </div>
            </div>
        `;

        const input = container.querySelector("#impact-target-input");
        const btn = container.querySelector("#btn-run-simulation");
        const resultsTarget = container.querySelector("#impact-results-target");

        const runSim = async (targetPath) => {
            if (!targetPath) return;
            try {
                btn.disabled = true;
                btn.innerHTML = `<span>⏳</span><span>Simulating...</span>`;
                const res = await api.simulateImpact(activeProj.id, { target_file_path: targetPath });
                DiffViewerComponent.renderImpactSummary(resultsTarget, res.data);
            } catch (err) {
                ToastManager.error(err.message || "Simulation failed.");
            } finally {
                btn.disabled = false;
                btn.innerHTML = `<span>💥</span><span>Calculate Blast Radius</span>`;
            }
        };

        btn.addEventListener("click", () => runSim(input.value.trim()));
        input.addEventListener("keydown", (e) => {
            if (e.key === "Enter") runSim(input.value.trim());
        });

        const activeFile = store.getState().activeFile;
        if (activeFile?.path) {
            input.value = activeFile.path;
            runSim(activeFile.path);
        }
    }
}
