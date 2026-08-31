import { api } from "../api.js";
import { store } from "../store.js";

export class CommandPalette {
    static init() {
        const modal = document.getElementById("command-palette-modal");
        const input = document.getElementById("command-palette-input");
        const resultsContainer = document.getElementById("command-palette-results");
        const triggerBtn = document.getElementById("btn-quick-search");

        if (!modal || !input || !resultsContainer) return;

        const open = () => {
            modal.classList.add("active");
            input.value = "";
            input.focus();
            this.renderInitialActions(resultsContainer);
        };

        const close = () => {
            modal.classList.remove("active");
        };

        triggerBtn?.addEventListener("click", open);

        // Global hotkey Ctrl+K / Cmd+K
        window.addEventListener("keydown", (e) => {
            if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k") {
                e.preventDefault();
                modal.classList.contains("active") ? close() : open();
            } else if (e.key === "Escape" && modal.classList.contains("active")) {
                close();
            }
        });

        modal.addEventListener("click", (e) => {
            if (e.target === modal) close();
        });

        let debounceTimer;
        input.addEventListener("input", () => {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(async () => {
                const query = input.value.trim();
                if (!query) {
                    this.renderInitialActions(resultsContainer);
                    return;
                }

                const activeProj = store.getState().activeProject;
                if (!activeProj) {
                    resultsContainer.innerHTML = `<div style="padding: 16px; color: var(--text-muted); text-align: center;">No active project selected.</div>`;
                    return;
                }

                try {
                    const res = await api.search(activeProj.id, { query, limit: 10 });
                    this.renderSearchResults(resultsContainer, res.data, close);
                } catch (err) {
                    resultsContainer.innerHTML = `<div style="padding: 16px; color: var(--accent-rose); text-align: center;">${err.message}</div>`;
                }
            }, 250);
        });
    }

    static renderInitialActions(container) {
        const actions = [
            { icon: "📂", label: "Open File Intelligence", hash: "#/workspace" },
            { icon: "🏗️", label: "Explore Architecture Layers", hash: "#/architecture" },
            { icon: "🕸️", label: "View Dependency Graph", hash: "#/dependencies" },
            { icon: "⚡", label: "Trace Code Flows", hash: "#/flows" },
            { icon: "💥", label: "Simulate Change Blast Radius", hash: "#/impact" },
            { icon: "🩺", label: "Check Code Health & Hotspots", hash: "#/health" },
            { icon: "🧭", label: "Open Onboarding Tour", hash: "#/onboarding" },
            { icon: "🤖", label: "Ask AI Codebase Copilot", hash: "#/copilot" },
        ];

        container.innerHTML = `
            <div style="font-size: 11px; font-weight: 600; color: var(--text-muted); padding: 6px 12px; text-transform: uppercase;">
                Navigation Quick Actions
            </div>
            ${actions.map(a => `
                <a href="${a.hash}" class="palette-item flex items-center gap-3" style="padding: 10px 12px; border-radius: var(--radius-sm); color: var(--text-primary); transition: background var(--transition-fast);">
                    <span>${a.icon}</span>
                    <span style="font-size: 13px; font-weight: 500;">${a.label}</span>
                </a>
            `).join("")}
        `;

        container.querySelectorAll(".palette-item").forEach(el => {
            el.addEventListener("click", () => {
                document.getElementById("command-palette-modal")?.classList.remove("active");
            });
        });
    }

    static renderSearchResults(container, searchData, closeCallback) {
        const { files = [], symbols = [], functions = [] } = searchData.results;
        const total = files.length + symbols.length + functions.length;

        if (total === 0) {
            container.innerHTML = `<div style="padding: 24px; color: var(--text-muted); text-align: center;">No matches found.</div>`;
            return;
        }

        let html = "";

        if (files.length > 0) {
            html += `<div style="font-size: 11px; font-weight: 600; color: var(--text-muted); padding: 6px 12px; text-transform: uppercase;">Files (${files.length})</div>`;
            html += files.map(f => `
                <div class="palette-item flex items-center justify-between" style="padding: 8px 12px; border-radius: var(--radius-sm); cursor: pointer;" data-path="${f.path}">
                    <div class="flex items-center gap-2">
                        <span>📄</span>
                        <span class="font-mono text-sm">${f.path}</span>
                    </div>
                    <span class="badge badge-layer-${f.layer}">${f.layer}</span>
                </div>
            `).join("");
        }

        if (functions.length > 0) {
            html += `<div style="font-size: 11px; font-weight: 600; color: var(--text-muted); padding: 6px 12px; margin-top: 8px; text-transform: uppercase;">Functions (${functions.length})</div>`;
            html += functions.map(fn => `
                <div class="palette-item flex items-center justify-between" style="padding: 8px 12px; border-radius: var(--radius-sm); cursor: pointer;" data-path="${fn.file_path}" data-line="${fn.start_line}">
                    <div class="flex items-center gap-2">
                        <span style="color: var(--accent-violet);">ƒ</span>
                        <span class="font-mono text-sm">${fn.qualified_name}()</span>
                    </div>
                    <span class="text-xs text-muted">${fn.file_path}:${fn.start_line}</span>
                </div>
            `).join("");
        }

        container.innerHTML = html;

        container.querySelectorAll(".palette-item").forEach(item => {
            item.addEventListener("click", () => {
                const path = item.getAttribute("data-path");
                const line = item.getAttribute("data-line");
                if (path) {
                    store.setActiveFile({ path, line: line ? parseInt(line, 10) : 1 });
                    window.location.hash = "#/workspace";
                }
                closeCallback();
            });
        });
    }
}
