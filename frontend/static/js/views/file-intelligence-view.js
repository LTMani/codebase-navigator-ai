import { api } from "../api.js";
import { ToastManager } from "../components/toast.js";
import { store } from "../store.js";

export class FileIntelligenceView {
    async render(container) {
        const activeProj = store.getState().activeProject;
        if (!activeProj) {
            container.innerHTML = `<div class="card text-center">Please select a project first.</div>`;
            return;
        }

        container.innerHTML = `
            <div class="flex flex-col gap-6">
                <div>
                    <h2 style="font-size: 20px; font-weight: 700; margin-bottom: 4px;">File Intelligence & Outline</h2>
                    <p class="text-secondary text-xs">Deep AST symbol outlines, class definitions, function signatures, and imports.</p>
                </div>

                <div class="card flex items-center gap-3">
                    <span class="text-xs text-muted font-bold">SELECT FILE:</span>
                    <input type="text" id="intel-file-search" class="input-field text-xs font-mono" placeholder="Enter relative path e.g. services/auth_service.py..." />
                    <button id="btn-load-intel" class="btn btn-primary btn-sm">Inspect</button>
                </div>

                <div id="intel-results-target">
                    <div class="text-center text-secondary" style="padding: 48px 0;">
                        Enter a file path above or pick one from the workspace explorer.
                    </div>
                </div>
            </div>
        `;

        const input = container.querySelector("#intel-file-search");
        const loadBtn = container.querySelector("#btn-load-intel");
        const resultsTarget = container.querySelector("#intel-results-target");

        const inspectFile = async (filePath) => {
            if (!filePath) return;
            try {
                const res = await api.getFileIntelligence(activeProj.id, filePath);
                this.renderDetails(resultsTarget, res.data);
            } catch (err) {
                ToastManager.error(err.message || "File not found.");
            }
        };

        loadBtn.addEventListener("click", () => inspectFile(input.value.trim()));
        input.addEventListener("keydown", (e) => {
            if (e.key === "Enter") inspectFile(input.value.trim());
        });

        const activeFile = store.getState().activeFile;
        if (activeFile?.path) {
            input.value = activeFile.path;
            inspectFile(activeFile.path);
        }
    }

    renderDetails(container, data) {
        const { file, symbols = [], functions = [], classes = [], imports = [], dependents = [] } = data;

        container.innerHTML = `
            <div class="flex flex-col gap-6">
                <!-- Overview Header Card -->
                <div class="card flex items-center justify-between" style="border-left: 4px solid var(--layer-${file.layer_classification});">
                    <div class="flex flex-col gap-1">
                        <div class="flex items-center gap-3">
                            <h3 style="font-size: 18px; font-weight: 700;" class="font-mono">${file.filename}</h3>
                            <span class="badge badge-layer-${file.layer_classification}">${file.layer_classification}</span>
                        </div>
                        <span class="font-mono text-xs text-muted">${file.relative_path}</span>
                    </div>
                    <div class="flex items-center gap-4 font-mono text-xs">
                        <div>Lines: <span class="text-primary font-bold">${file.total_lines}</span></div>
                        <div>Complexity: <span class="text-primary font-bold">${file.cyclomatic_complexity}</span></div>
                        <div>Maintainability: <span class="text-accent font-bold">${file.maintainability_index}/100</span></div>
                    </div>
                </div>

                <!-- 2-Column Symbols and Dependencies -->
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                    <!-- Left: Classes & Functions -->
                    <div class="card flex flex-col gap-4">
                        <h4 style="font-size: 14px; font-weight: 600;">Extracted Classes (${classes.length})</h4>
                        ${classes.map(c => `
                            <div class="card flex flex-col gap-1" style="background: var(--bg-tertiary); padding: 12px;">
                                <div class="flex items-center justify-between font-mono text-xs">
                                    <span style="font-weight: 700; color: var(--accent-amber);">🔷 ${c.name}</span>
                                    <span class="text-muted">Lines ${c.start_line}-${c.end_line}</span>
                                </div>
                                ${c.docstring ? `<p class="text-xs text-secondary" style="margin-top: 4px;">${c.docstring}</p>` : ''}
                            </div>
                        `).join("")}

                        <h4 style="font-size: 14px; font-weight: 600; margin-top: 12px;">Extracted Functions (${functions.length})</h4>
                        ${functions.map(fn => `
                            <div class="card flex flex-col gap-1" style="background: var(--bg-tertiary); padding: 10px;">
                                <div class="flex items-center justify-between font-mono text-xs">
                                    <span style="font-weight: 600; color: var(--accent-violet);">ƒ ${fn.name}()</span>
                                    <span class="text-muted">Lines ${fn.start_line}-${fn.end_line}</span>
                                </div>
                                <div class="text-xs text-muted font-mono">Complexity: ${fn.cyclomatic_complexity}</div>
                            </div>
                        `).join("")}
                    </div>

                    <!-- Right: Imports & Dependents -->
                    <div class="card flex flex-col gap-4">
                        <h4 style="font-size: 14px; font-weight: 600;">Imported Modules (${imports.length})</h4>
                        <div class="flex flex-col gap-1">
                            ${imports.map(i => `
                                <div class="font-mono text-xs text-secondary" style="padding: 4px 8px; background: var(--bg-tertiary); border-radius: var(--radius-sm);">
                                    📦 ${i.module_name} ${i.imported_symbols?.length ? `(${i.imported_symbols.join(", ")})` : ''}
                                </div>
                            `).join("")}
                        </div>

                        <h4 style="font-size: 14px; font-weight: 600; margin-top: 12px;">Downstream Dependents (${dependents.length})</h4>
                        <div class="flex flex-col gap-1">
                            ${dependents.map(d => `
                                <div class="font-mono text-xs text-accent" style="padding: 4px 8px; background: rgba(59,130,246,0.05); border-radius: var(--radius-sm);">
                                    🔗 ${d.source_path}
                                </div>
                            `).join("")}
                        </div>
                    </div>
                </div>
            </div>
        `;
    }
}
