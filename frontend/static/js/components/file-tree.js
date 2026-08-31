import { store } from "../store.js";

export class FileTreeComponent {
    constructor(container, onSelectFile) {
        this.container = container;
        this.onSelectFile = onSelectFile;
        this.searchFilter = "";
    }

    render(treeData) {
        if (!this.container || !treeData) return;

        this.container.innerHTML = `
            <div class="flex flex-col h-full">
                <div style="padding: 12px; border-bottom: 1px solid var(--border-color);">
                    <input type="text" id="tree-search-input" class="input-field text-xs" placeholder="Filter files..." value="${this.searchFilter}" />
                </div>
                <div id="tree-nodes-container" class="flex-1" style="overflow-y: auto; padding: 8px 6px;">
                    <!-- Recursive Tree Nodes -->
                </div>
            </div>
        `;

        const searchInput = this.container.querySelector("#tree-search-input");
        searchInput.addEventListener("input", (e) => {
            this.searchFilter = e.target.value.toLowerCase().trim();
            this.renderNodes(this.container.querySelector("#tree-nodes-container"), treeData);
        });

        this.renderNodes(this.container.querySelector("#tree-nodes-container"), treeData);
    }

    renderNodes(container, rootNode) {
        if (!container || !rootNode) return;
        container.innerHTML = "";

        const createNodeElement = (node, depth = 0) => {
            const isDir = node.type === "directory";
            const el = document.createElement("div");
            el.className = "tree-node";
            el.style.paddingLeft = `${depth * 14 + 6}px`;

            if (isDir) {
                // Check if any children match search filter
                if (this.searchFilter && !this._nodeHasMatch(node, this.searchFilter)) {
                    return null;
                }

                const dirHeader = document.createElement("div");
                dirHeader.className = "flex items-center gap-2";
                dirHeader.style.padding = "4px 6px";
                dirHeader.style.borderRadius = "var(--radius-sm)";
                dirHeader.style.cursor = "pointer";
                dirHeader.style.fontSize = "12px";
                dirHeader.style.fontWeight = "600";
                dirHeader.style.color = "var(--text-secondary)";

                dirHeader.innerHTML = `
                    <span class="tree-arrow" style="font-size: 10px; transition: transform 0.2s;">▼</span>
                    <span>📁</span>
                    <span class="truncate">${node.name}</span>
                `;

                const childrenContainer = document.createElement("div");
                childrenContainer.className = "tree-children";

                let isExpanded = true;
                dirHeader.addEventListener("click", () => {
                    isExpanded = !isExpanded;
                    childrenContainer.style.display = isExpanded ? "block" : "none";
                    dirHeader.querySelector(".tree-arrow").style.transform = isExpanded ? "rotate(0deg)" : "rotate(-90deg)";
                });

                el.appendChild(dirHeader);
                el.appendChild(childrenContainer);

                if (node.children) {
                    for (const child of node.children) {
                        const childEl = createNodeElement(child, depth + 1);
                        if (childEl) childrenContainer.appendChild(childEl);
                    }
                }
            } else {
                // File Node
                if (this.searchFilter && !node.name.toLowerCase().includes(this.searchFilter) && !node.path.toLowerCase().includes(this.searchFilter)) {
                    return null;
                }

                const fileItem = document.createElement("div");
                fileItem.className = "tree-file flex items-center justify-between";
                fileItem.style.padding = "4px 6px";
                fileItem.style.borderRadius = "var(--radius-sm)";
                fileItem.style.cursor = "pointer";
                fileItem.style.fontSize = "12px";
                fileItem.style.color = "var(--text-primary)";
                fileItem.style.transition = "background var(--transition-fast)";

                const icon = this._getFileIcon(node.extension);

                fileItem.innerHTML = `
                    <div class="flex items-center gap-2 truncate">
                        <span>${icon}</span>
                        <span class="font-mono text-xs truncate">${node.name}</span>
                    </div>
                    ${node.layer ? `<span class="badge badge-layer-${node.layer}" style="font-size: 9px; padding: 1px 4px;">${node.layer.slice(0, 3)}</span>` : ""}
                `;

                fileItem.addEventListener("click", () => {
                    container.querySelectorAll(".tree-file").forEach(f => f.style.backgroundColor = "transparent");
                    fileItem.style.backgroundColor = "var(--bg-active)";
                    if (this.onSelectFile) {
                        this.onSelectFile(node);
                    }
                });

                el.appendChild(fileItem);
            }

            return el;
        };

        if (rootNode.children) {
            for (const child of rootNode.children) {
                const nodeEl = createNodeElement(child, 0);
                if (nodeEl) container.appendChild(nodeEl);
            }
        }
    }

    _nodeHasMatch(dirNode, filter) {
        if (!dirNode.children) return false;
        for (const child of dirNode.children) {
            if (child.name.toLowerCase().includes(filter) || child.path?.toLowerCase().includes(filter)) {
                return true;
            }
            if (child.type === "directory" && this._nodeHasMatch(child, filter)) {
                return true;
            }
        }
        return false;
    }

    _getFileIcon(ext) {
        const map = {
            ".py": "🐍",
            ".js": "🟨",
            ".jsx": "⚛️",
            ".ts": "🔷",
            ".tsx": "⚛️",
            ".html": "🌐",
            ".css": "🎨",
            ".json": "📋",
            ".md": "📝",
            ".toml": "⚙️",
        };
        return map[ext?.toLowerCase()] || "📄";
    }
}
