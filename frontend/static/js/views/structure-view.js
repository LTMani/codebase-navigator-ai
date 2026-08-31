import { api } from "../api.js";
import { FileTreeComponent } from "../components/file-tree.js";
import { ToastManager } from "../components/toast.js";
import { store } from "../store.js";

export class StructureView {
    async render(container) {
        const activeProj = store.getState().activeProject;
        if (!activeProj) {
            container.innerHTML = `<div class="card text-center">Please select a project first.</div>`;
            return;
        }

        container.innerHTML = `
            <div class="flex flex-col gap-6">
                <div>
                    <h2 style="font-size: 20px; font-weight: 700; margin-bottom: 4px;">Codebase Structure Explorer</h2>
                    <p class="text-secondary text-xs">Hierarchical directory map, file distribution, and depth metrics.</p>
                </div>

                <div style="display: grid; grid-template-columns: 1fr 2fr; gap: 20px;">
                    <!-- Left: Interactive Tree -->
                    <div class="card" style="height: 600px; display: flex; flex-direction: column;">
                        <div style="font-size: 13px; font-weight: 600; margin-bottom: 12px;">Directory Hierarchy</div>
                        <div id="structure-tree-target" class="flex-1" style="overflow-y: auto;"></div>
                    </div>

                    <!-- Right: Selected Node Details -->
                    <div class="card flex flex-col gap-4" id="structure-node-details">
                        <div class="text-center text-secondary" style="padding: 48px 0;">
                            Select a directory or file in the tree to view metrics, complexity, and layer classification.
                        </div>
                    </div>
                </div>
            </div>
        `;

        const treeTarget = container.querySelector("#structure-tree-target");
        const detailsTarget = container.querySelector("#structure-node-details");

        const fileTree = new FileTreeComponent(treeTarget, (selectedNode) => {
            this.renderSelectedNodeDetails(detailsTarget, selectedNode, activeProj);
        });

        try {
            const treeRes = await api.getProjectTree(activeProj.id);
            fileTree.render(treeRes.data.tree);
        } catch (err) {
            ToastManager.error("Failed to load project tree.");
        }
    }

    renderSelectedNodeDetails(container, node, project) {
        container.innerHTML = `
            <div class="flex flex-col gap-4">
                <div class="flex items-center justify-between" style="border-bottom: 1px solid var(--border-color); padding-bottom: 16px;">
                    <div class="flex items-center gap-3">
                        <span style="font-size: 24px;">${node.type === 'directory' ? '📁' : '📄'}</span>
                        <div class="flex flex-col">
                            <h3 style="font-size: 16px; font-weight: 700;">${node.name}</h3>
                            <span class="font-mono text-xs text-muted">${node.path || '/'}</span>
                        </div>
                    </div>
                    ${node.layer ? `<span class="badge badge-layer-${node.layer}">${node.layer}</span>` : ''}
                </div>

                <div class="dashboard-metrics-grid">
                    <div class="metric-card">
                        <div>
                            <div class="metric-value">${node.lines || 0}</div>
                            <div class="metric-label">Total Lines</div>
                        </div>
                    </div>
                    <div class="metric-card">
                        <div>
                            <div class="metric-value">${node.complexity || 1}</div>
                            <div class="metric-label">Cyclomatic Complexity</div>
                        </div>
                    </div>
                    <div class="metric-card">
                        <div>
                            <div class="metric-value">${node.maintainability || 100} / 100</div>
                            <div class="metric-label">Maintainability</div>
                        </div>
                    </div>
                </div>

                <div class="card flex flex-col gap-2" style="background: var(--bg-tertiary);">
                    <span style="font-size: 11px; font-weight: 700; color: var(--text-muted); text-transform: uppercase;">ACTIONS</span>
                    <div class="flex items-center gap-3">
                        <button id="btn-open-in-editor" class="btn btn-primary btn-sm">💻 Open in Workspace</button>
                        <a href="#/impact" class="btn btn-secondary btn-sm">💥 Check Blast Radius</a>
                    </div>
                </div>
            </div>
        `;

        container.querySelector("#btn-open-in-editor")?.addEventListener("click", () => {
            store.setActiveFile({ path: node.path });
            window.location.hash = "#/workspace";
        });
    }
}
