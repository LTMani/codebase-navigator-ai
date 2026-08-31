import { api } from "../api.js";
import { DrawerManager } from "../components/drawer.js";
import { GraphCanvasComponent } from "../components/graph-canvas.js";
import { ToastManager } from "../components/toast.js";
import { store } from "../store.js";

export class DependencyView {
    async render(container) {
        const activeProj = store.getState().activeProject;
        if (!activeProj) {
            container.innerHTML = `<div class="card text-center">Please select a project first.</div>`;
            return;
        }

        container.innerHTML = `
            <div class="flex flex-col h-full gap-4">
                <div class="flex items-center justify-between flex-shrink-0">
                    <div>
                        <h2 style="font-size: 20px; font-weight: 700; margin-bottom: 4px;">Dependency Graph Explorer</h2>
                        <p class="text-secondary text-xs">
                            Interactive force-directed graph with Tarjan cycle detection and PageRank centrality.
                        </p>
                    </div>
                    <div class="flex items-center gap-3">
                        <a href="#/circular" class="btn btn-outline btn-sm">🔁 View Cycles</a>
                        <button id="btn-refresh-dep" class="btn btn-secondary btn-sm">🔄 Rebuild Graph</button>
                    </div>
                </div>

                <!-- Canvas Graph Viewport -->
                <div class="card flex-1 p-0 overflow-hidden" style="min-height: 540px; position: relative;" id="graph-viewport-target">
                    <!-- Canvas Injected Here -->
                </div>
            </div>
        `;

        const viewportTarget = container.querySelector("#graph-viewport-target");

        const graphEngine = new GraphCanvasComponent(viewportTarget, async (selectedNode) => {
            try {
                const intelRes = await api.getFileIntelligence(activeProj.id, selectedNode.path);
                const fileData = intelRes.data;

                DrawerManager.open(`File Intelligence: ${selectedNode.name}`, `
                    <div class="flex flex-col gap-4">
                        <div class="card flex flex-col gap-2" style="padding: 12px;">
                            <div class="flex items-center justify-between">
                                <span class="font-mono text-xs font-bold truncate">${fileData.file.filename}</span>
                                <span class="badge badge-layer-${fileData.file.layer_classification}">${fileData.file.layer_classification}</span>
                            </div>
                            <div style="font-size: 11px;" class="text-secondary">
                                PageRank Centrality: <span class="font-mono text-primary">${selectedNode.pagerank?.toFixed(3) || '0.000'}</span>
                            </div>
                        </div>

                        <div class="flex items-center gap-3">
                            <button id="drawer-btn-open-workspace" class="btn btn-primary btn-sm w-full">💻 Open in Workspace</button>
                        </div>
                    </div>
                `);

                document.getElementById("drawer-btn-open-workspace")?.addEventListener("click", () => {
                    DrawerManager.close();
                    store.setActiveFile({ path: selectedNode.path });
                    window.location.hash = "#/workspace";
                });
            } catch (err) {
                console.error("Failed to load node intelligence", err);
            }
        });

        const loadGraph = async () => {
            try {
                const res = await api.getDependencies(activeProj.id);
                graphEngine.render(res.data);
            } catch (err) {
                ToastManager.error("Failed to load dependency graph.");
            }
        };

        container.querySelector("#btn-refresh-dep")?.addEventListener("click", loadGraph);
        loadGraph();
    }
}
