import { api } from "../api.js";
import { CodeViewerComponent } from "../components/code-viewer.js";
import { DrawerManager } from "../components/drawer.js";
import { FileTreeComponent } from "../components/file-tree.js";
import { ToastManager } from "../components/toast.js";
import { store } from "../store.js";

export class WorkspaceView {
    async render(container) {
        const activeProj = store.getState().activeProject;
        if (!activeProj) {
            container.innerHTML = `
                <div class="card text-center" style="padding: 48px;">
                    <h3 style="font-size: 18px; font-weight: 600; margin-bottom: 8px;">No Project Selected</h3>
                    <p class="text-secondary text-sm" style="margin-bottom: 16px;">Please import or select a project to view workspace.</p>
                    <a href="#/import" class="btn btn-primary">Import Project</a>
                </div>
            `;
            return;
        }

        container.innerHTML = `
            <div class="split-pane-layout">
                <!-- Left File Tree -->
                <div class="split-pane-sidebar" id="workspace-tree-sidebar">
                    <div class="flex items-center justify-between" style="padding: 12px 16px; border-bottom: 1px solid var(--border-color); background: rgba(0,0,0,0.1);">
                        <span style="font-size: 11px; font-weight: 700; color: var(--text-muted); text-transform: uppercase;">EXPLORER</span>
                        <button id="btn-refresh-tree" class="btn btn-outline btn-sm" title="Refresh Tree">🔄</button>
                    </div>
                    <div id="workspace-tree-target" class="flex-1" style="overflow-y: auto;"></div>
                </div>

                <!-- Center Code Viewer -->
                <div class="split-pane-content" id="workspace-editor-target">
                    <div class="flex items-center justify-center h-full text-secondary">
                        Select a file from the explorer to inspect code and AST symbols.
                    </div>
                </div>

                <!-- Right Intelligence Drawer Panel -->
                <div class="split-pane-drawer" id="workspace-intelligence-panel">
                    <div class="flex items-center justify-between" style="padding: 12px 16px; border-bottom: 1px solid var(--border-color); background: rgba(0,0,0,0.1);">
                        <span style="font-size: 11px; font-weight: 700; color: var(--text-muted); text-transform: uppercase;">CODE INTELLIGENCE</span>
                    </div>
                    <div id="workspace-intelligence-content" class="flex-1" style="overflow-y: auto; padding: 16px;">
                        <div class="text-xs text-muted text-center" style="padding: 24px 0;">
                            No file selected.
                        </div>
                    </div>
                </div>
            </div>
        `;

        const treeTarget = container.querySelector("#workspace-tree-target");
        const editorTarget = container.querySelector("#workspace-editor-target");
        const intelTarget = container.querySelector("#workspace-intelligence-content");

        const codeViewer = new CodeViewerComponent(editorTarget);

        const loadFileDetails = async (filePath, targetLine = null) => {
            try {
                const [contentRes, intelRes] = await Promise.all([
                    api.getFileContent(activeProj.id, filePath),
                    api.getFileIntelligence(activeProj.id, filePath),
                ]);

                codeViewer.render(filePath, contentRes.data.content, targetLine);
                this.renderFileIntelligence(intelTarget, intelRes.data, (line) => {
                    codeViewer.render(filePath, contentRes.data.content, line);
                });
            } catch (err) {
                ToastManager.error(`Failed to load file: ${err.message}`);
            }
        };

        const fileTree = new FileTreeComponent(treeTarget, (fileNode) => {
            loadFileDetails(fileNode.path);
        });

        // Load project tree
        try {
            const treeRes = await api.getProjectTree(activeProj.id);
            store.setProjectTree(treeRes.data.tree);
            fileTree.render(treeRes.data.tree);

            // Auto-load activeFile from store if present
            const activeFile = store.getState().activeFile;
            if (activeFile?.path) {
                loadFileDetails(activeFile.path, activeFile.line);
            }
        } catch (err) {
            ToastManager.error("Failed to load project structure.");
        }
    }

    renderFileIntelligence(container, data, onJumpLine) {
        if (!container || !data) return;
        const { file, symbols = [], functions = [], classes = [], dependencies = [], dependents = [] } = data;

        container.innerHTML = `
            <div class="flex flex-col gap-4">
                <!-- File Meta Card -->
                <div class="card flex flex-col gap-2" style="padding: 12px;">
                    <div class="flex items-center justify-between">
                        <span class="font-mono text-xs font-bold truncate">${file.filename}</span>
                        <span class="badge badge-layer-${file.layer_classification}">${file.layer_classification}</span>
                    </div>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 6px; font-size: 11px;" class="text-secondary">
                        <div>Lines: <span class="font-mono text-primary">${file.total_lines}</span></div>
                        <div>Complexity: <span class="font-mono text-primary">${file.cyclomatic_complexity}</span></div>
                        <div>Maintainability: <span class="font-mono text-primary">${file.maintainability_index}/100</span></div>
                        <div>Doc Ratio: <span class="font-mono text-primary">${(file.documentation_ratio * 100).toFixed(0)}%</span></div>
                    </div>
                </div>

                <!-- Classes Outline -->
                ${classes.length > 0 ? `
                    <div class="flex flex-col gap-2">
                        <span style="font-size: 11px; font-weight: 700; color: var(--text-muted); text-transform: uppercase;">CLASSES (${classes.length})</span>
                        ${classes.map(c => `
                            <div class="flex items-center justify-between font-mono text-xs jump-line-btn" style="padding: 6px 8px; background: var(--bg-tertiary); border-radius: var(--radius-sm); cursor: pointer;" data-line="${c.start_line}">
                                <div class="flex items-center gap-2">
                                    <span style="color: var(--accent-amber);">🔷</span>
                                    <span style="font-weight: 600;">${c.name}</span>
                                </div>
                                <span class="text-muted">:${c.start_line}</span>
                            </div>
                        `).join("")}
                    </div>
                ` : ''}

                <!-- Functions Outline -->
                ${functions.length > 0 ? `
                    <div class="flex flex-col gap-2">
                        <span style="font-size: 11px; font-weight: 700; color: var(--text-muted); text-transform: uppercase;">FUNCTIONS (${functions.length})</span>
                        ${functions.map(fn => `
                            <div class="flex items-center justify-between font-mono text-xs jump-line-btn" style="padding: 6px 8px; background: var(--bg-tertiary); border-radius: var(--radius-sm); cursor: pointer;" data-line="${fn.start_line}">
                                <div class="flex items-center gap-2">
                                    <span style="color: var(--accent-violet);">ƒ</span>
                                    <span style="font-weight: 600;">${fn.name}()</span>
                                </div>
                                <span class="text-muted">:${fn.start_line}</span>
                            </div>
                        `).join("")}
                    </div>
                ` : ''}

                <!-- Dependents (Who uses this file?) -->
                <div class="flex flex-col gap-2">
                    <span style="font-size: 11px; font-weight: 700; color: var(--text-muted); text-transform: uppercase;">USED BY (${dependents.length})</span>
                    ${dependents.length > 0 ? dependents.map(d => `
                        <div class="font-mono text-xs truncate text-secondary" style="padding: 4px 6px; background: rgba(255,255,255,0.03); border-radius: var(--radius-sm);">
                            🔗 ${d.source_path}
                        </div>
                    `).join("") : '<div class="text-xs text-muted">No external dependents.</div>'}
                </div>
            </div>
        `;

        container.querySelectorAll(".jump-line-btn").forEach(btn => {
            btn.addEventListener("click", () => {
                const line = parseInt(btn.getAttribute("data-line"), 10);
                if (line && onJumpLine) {
                    onJumpLine(line);
                }
            });
        });
    }
}
