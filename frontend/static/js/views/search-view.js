import { api } from "../api.js";
import { ToastManager } from "../components/toast.js";
import { store } from "../store.js";

export class SearchView {
    render(container) {
        const activeProj = store.getState().activeProject;
        if (!activeProj) {
            container.innerHTML = `<div class="card text-center">Please select a project first.</div>`;
            return;
        }

        container.innerHTML = `
            <div class="flex flex-col gap-6">
                <div>
                    <h2 style="font-size: 20px; font-weight: 700; margin-bottom: 4px;">Advanced Code Search</h2>
                    <p class="text-secondary text-xs">Search files, classes, function signatures, and source content.</p>
                </div>

                <div class="card flex flex-col gap-4">
                    <div class="flex items-center gap-3">
                        <input type="text" id="global-search-input" class="input-field font-mono text-sm" placeholder="Search by name, docstring, or snippet..." />
                        <button id="btn-execute-search" class="btn btn-primary">🔍 Search</button>
                    </div>

                    <div class="flex items-center gap-4 text-xs">
                        <label class="flex items-center gap-2 cursor-pointer">
                            <input type="radio" name="search-scope" value="all" checked /> All Scopes
                        </label>
                        <label class="flex items-center gap-2 cursor-pointer">
                            <input type="radio" name="search-scope" value="files" /> Files
                        </label>
                        <label class="flex items-center gap-2 cursor-pointer">
                            <input type="radio" name="search-scope" value="functions" /> Functions
                        </label>
                        <label class="flex items-center gap-2 cursor-pointer">
                            <input type="radio" name="search-scope" value="classes" /> Classes
                        </label>
                    </div>
                </div>

                <div id="search-results-target">
                    <div class="text-center text-secondary" style="padding: 48px 0;">
                        Enter a search keyword above.
                    </div>
                </div>
            </div>
        `;

        const input = container.querySelector("#global-search-input");
        const btn = container.querySelector("#btn-execute-search");
        const resultsTarget = container.querySelector("#search-results-target");

        const executeSearch = async () => {
            const query = input.value.trim();
            if (!query) return;

            const scope = container.querySelector("input[name='search-scope']:checked")?.value || "all";

            try {
                btn.disabled = true;
                const res = await api.search(activeProj.id, { query, search_type: scope });
                this.renderResults(resultsTarget, res.data);
            } catch (err) {
                ToastManager.error(err.message || "Search query failed.");
            } finally {
                btn.disabled = false;
            }
        };

        btn.addEventListener("click", executeSearch);
        input.addEventListener("keydown", (e) => {
            if (e.key === "Enter") executeSearch();
        });
    }

    renderResults(container, searchData) {
        const { total_results = 0, results = {} } = searchData;
        const { files = [], functions = [], classes = [], content = [] } = results;

        if (total_results === 0) {
            container.innerHTML = `<div class="card text-center text-secondary" style="padding: 48px 0;">No matching entities found.</div>`;
            return;
        }

        container.innerHTML = `
            <div class="flex flex-col gap-6">
                <div class="text-xs text-muted font-bold uppercase">Found ${total_results} Matches</div>

                ${files.length > 0 ? `
                    <div class="card flex flex-col gap-2">
                        <h4 style="font-size: 14px; font-weight: 600;">Files (${files.length})</h4>
                        ${files.map(f => `
                            <div class="flex items-center justify-between font-mono text-xs search-hit-file" style="padding: 8px 12px; background: var(--bg-tertiary); border-radius: var(--radius-sm); cursor: pointer;" data-path="${f.path}">
                                <div class="flex items-center gap-2">
                                    <span>📄</span>
                                    <span>${f.path}</span>
                                </div>
                                <span class="badge badge-layer-${f.layer}">${f.layer}</span>
                            </div>
                        `).join("")}
                    </div>
                ` : ''}

                ${functions.length > 0 ? `
                    <div class="card flex flex-col gap-2">
                        <h4 style="font-size: 14px; font-weight: 600;">Functions (${functions.length})</h4>
                        ${functions.map(fn => `
                            <div class="flex items-center justify-between font-mono text-xs search-hit-file" style="padding: 8px 12px; background: var(--bg-tertiary); border-radius: var(--radius-sm); cursor: pointer;" data-path="${fn.file_path}" data-line="${fn.start_line}">
                                <div class="flex items-center gap-2">
                                    <span style="color: var(--accent-violet);">ƒ</span>
                                    <span style="font-weight: 600;">${fn.qualified_name}()</span>
                                </div>
                                <span class="text-muted">${fn.file_path}:${fn.start_line}</span>
                            </div>
                        `).join("")}
                    </div>
                ` : ''}

                ${classes.length > 0 ? `
                    <div class="card flex flex-col gap-2">
                        <h4 style="font-size: 14px; font-weight: 600;">Classes (${classes.length})</h4>
                        ${classes.map(c => `
                            <div class="flex items-center justify-between font-mono text-xs search-hit-file" style="padding: 8px 12px; background: var(--bg-tertiary); border-radius: var(--radius-sm); cursor: pointer;" data-path="${c.file_path}" data-line="${c.start_line}">
                                <div class="flex items-center gap-2">
                                    <span style="color: var(--accent-amber);">🔷</span>
                                    <span style="font-weight: 600;">${c.name}</span>
                                </div>
                                <span class="text-muted">${c.file_path}:${c.start_line}</span>
                            </div>
                        `).join("")}
                    </div>
                ` : ''}
            </div>
        `;

        container.querySelectorAll(".search-hit-file").forEach(el => {
            el.addEventListener("click", () => {
                const path = el.getAttribute("data-path");
                const line = el.getAttribute("data-line");
                store.setActiveFile({ path, line: line ? parseInt(line, 10) : 1 });
                window.location.hash = "#/workspace";
            });
        });
    }
}
