export class GraphCanvasComponent {
    constructor(container, onSelectNode) {
        this.container = container;
        this.onSelectNode = onSelectNode;
        this.canvas = null;
        this.ctx = null;
        this.nodes = [];
        this.edges = [];
        this.cycles = [];
        this.selectedNode = null;
        this.hoveredNode = null;

        // Viewport transform
        this.transform = { x: 0, y: 0, scale: 1 };
        this.isDragging = false;
        this.draggedNode = null;
        this.lastMouse = { x: 0, y: 0 };
        this.animId = null;

        // Simulation parameters
        this.simulationRunning = true;
        this.alpha = 1.0;

        // Colors
        this.layerColors = {
            presentation: "#ec4899",
            api: "#8b5cf6",
            service: "#3b82f6",
            domain: "#10b981",
            repository: "#f59e0b",
            infrastructure: "#64748b",
            utility: "#06b6d4",
            general: "#94a3b8",
        };
    }

    render(graphData) {
        if (!this.container || !graphData) return;

        this.container.innerHTML = `
            <div class="graph-container">
                <canvas class="graph-canvas"></canvas>
                <div class="graph-toolbar">
                    <button id="btn-zoom-in" class="btn btn-secondary btn-sm" title="Zoom In">➕</button>
                    <button id="btn-zoom-out" class="btn btn-secondary btn-sm" title="Zoom Out">➖</button>
                    <button id="btn-reset-view" class="btn btn-secondary btn-sm" title="Reset View">🎯</button>
                    <button id="btn-toggle-sim" class="btn btn-secondary btn-sm" title="Pause/Resume Layout">⏯️</button>
                </div>
                <div class="graph-legend">
                    <div style="font-weight: 600; margin-bottom: 6px;">ARCHITECTURAL LAYERS</div>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 4px;">
                        ${Object.entries(this.layerColors).map(([k, c]) => `
                            <div class="flex items-center gap-1">
                                <span style="width: 8px; height: 8px; border-radius: 50%; background: ${c};"></span>
                                <span style="text-transform: capitalize; color: var(--text-secondary);">${k}</span>
                            </div>
                        `).join("")}
                    </div>
                </div>
                <div class="graph-tooltip"></div>
            </div>
        `;

        this.canvas = this.container.querySelector("canvas");
        this.ctx = this.canvas.getContext("2d");
        this.tooltip = this.container.querySelector(".graph-tooltip");

        this.resize();
        window.addEventListener("resize", () => this.resize());

        this.initData(graphData);
        this.initEvents();
        this.startSimulation();
    }

    resize() {
        if (!this.canvas) return;
        const rect = this.canvas.parentElement.getBoundingClientRect();
        this.canvas.width = rect.width * window.devicePixelRatio;
        this.canvas.height = rect.height * window.devicePixelRatio;
        this.ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
    }

    initData(graphData) {
        const rawNodes = graphData.nodes || [];
        const rawEdges = graphData.edges || [];
        this.cycles = graphData.cycles || [];

        const width = this.canvas.width / window.devicePixelRatio;
        const height = this.canvas.height / window.devicePixelRatio;

        // Position nodes randomly in center circle
        this.nodes = rawNodes.map((n, i) => {
            const angle = (i / max(rawNodes.length, 1)) * 2 * Math.PI;
            const radius = 100 + Math.random() * 150;
            return {
                ...n,
                x: width / 2 + Math.cos(angle) * radius,
                y: height / 2 + Math.sin(angle) * radius,
                vx: 0,
                vy: 0,
                radius: Math.max(6, Math.min(18, (n.pagerank || 0.1) * 20 + 6)),
                color: this.layerColors[n.layer] || this.layerColors.general,
            };
        });

        const nodeMap = new Map(this.nodes.map(n => [n.path, n]));

        this.edges = rawEdges.map(e => ({
            ...e,
            sourceNode: nodeMap.get(e.source),
            targetNode: nodeMap.get(e.target),
        })).filter(e => e.sourceNode && e.targetNode);

        // Center viewport
        this.transform = { x: 0, y: 0, scale: 1 };
        this.alpha = 1.0;
    }

    initEvents() {
        const c = this.canvas;

        c.addEventListener("mousedown", (e) => {
            const pos = this.getCanvasCoords(e);
            const hit = this.findNodeAt(pos.x, pos.y);

            if (hit) {
                this.draggedNode = hit;
                this.selectedNode = hit;
                if (this.onSelectNode) this.onSelectNode(hit);
            } else {
                this.isDragging = true;
            }
            this.lastMouse = { x: e.clientX, y: e.clientY };
        });

        window.addEventListener("mousemove", (e) => {
            if (this.draggedNode) {
                const pos = this.getCanvasCoords(e);
                this.draggedNode.x = pos.x;
                this.draggedNode.y = pos.y;
                this.alpha = 0.3; // Reheat simulation
            } else if (this.isDragging) {
                const dx = e.clientX - this.lastMouse.x;
                const dy = e.clientY - this.lastMouse.y;
                this.transform.x += dx;
                this.transform.y += dy;
                this.lastMouse = { x: e.clientX, y: e.clientY };
            }

            // Hover tooltip
            const pos = this.getCanvasCoords(e);
            const hit = this.findNodeAt(pos.x, pos.y);
            this.hoveredNode = hit;

            if (hit && this.tooltip) {
                this.tooltip.innerHTML = `
                    <div style="font-weight: 600;">${hit.name}</div>
                    <div class="text-xs text-muted font-mono">${hit.path}</div>
                    <div class="badge badge-layer-${hit.layer}" style="margin-top: 4px;">${hit.layer}</div>
                `;
                this.tooltip.style.left = `${e.clientX - this.canvas.getBoundingClientRect().left + 12}px`;
                this.tooltip.style.top = `${e.clientY - this.canvas.getBoundingClientRect().top + 12}px`;
                this.tooltip.classList.add("visible");
            } else if (this.tooltip) {
                this.tooltip.classList.remove("visible");
            }
        });

        window.addEventListener("mouseup", () => {
            this.isDragging = false;
            this.draggedNode = null;
        });

        c.addEventListener("wheel", (e) => {
            e.preventDefault();
            const zoomFactor = e.deltaY < 0 ? 1.1 : 0.9;
            this.transform.scale = Math.max(0.2, Math.min(3.5, this.transform.scale * zoomFactor));
        });

        // Toolbar buttons
        this.container.querySelector("#btn-zoom-in")?.addEventListener("click", () => {
            this.transform.scale = Math.min(3.5, this.transform.scale * 1.2);
        });
        this.container.querySelector("#btn-zoom-out")?.addEventListener("click", () => {
            this.transform.scale = Math.max(0.2, this.transform.scale / 1.2);
        });
        this.container.querySelector("#btn-reset-view")?.addEventListener("click", () => {
            this.transform = { x: 0, y: 0, scale: 1 };
        });
        this.container.querySelector("#btn-toggle-sim")?.addEventListener("click", () => {
            this.simulationRunning = !this.simulationRunning;
        });
    }

    getCanvasCoords(e) {
        const rect = this.canvas.getBoundingClientRect();
        const clientX = e.clientX - rect.left;
        const clientY = e.clientY - rect.top;
        return {
            x: (clientX - this.transform.x) / this.transform.scale,
            y: (clientY - this.transform.y) / this.transform.scale,
        };
    }

    findNodeAt(x, y) {
        for (const n of this.nodes) {
            const dist = Math.hypot(n.x - x, n.y - y);
            if (dist <= n.radius + 4) return n;
        }
        return null;
    }

    startSimulation() {
        const tick = () => {
            if (this.simulationRunning && this.alpha > 0.005) {
                this.stepSimulation();
                this.alpha *= 0.985;
            }
            this.draw();
            this.animId = requestAnimationFrame(tick);
        };
        tick();
    }

    stepSimulation() {
        const k = 80; // Ideal spring length

        // 1. Repulsion between all node pairs
        for (let i = 0; i < this.nodes.length; i++) {
            for (let j = i + 1; j < this.nodes.length; j++) {
                const n1 = this.nodes[i];
                const n2 = this.nodes[j];
                const dx = n2.x - n1.x;
                const dy = n2.y - n1.y;
                const dist = Math.hypot(dx, dy) || 1;
                const force = (k * k) / (dist * dist) * 1.5;

                const fx = (dx / dist) * force * this.alpha;
                const fy = (dy / dist) * force * this.alpha;

                if (n1 !== this.draggedNode) { n1.x -= fx; n1.y -= fy; }
                if (n2 !== this.draggedNode) { n2.x += fx; n2.y += fy; }
            }
        }

        // 2. Attraction along edges
        for (const e of this.edges) {
            const dx = e.targetNode.x - e.sourceNode.x;
            const dy = e.targetNode.y - e.sourceNode.y;
            const dist = Math.hypot(dx, dy) || 1;
            const force = (dist * dist) / k * 0.05;

            const fx = (dx / dist) * force * this.alpha;
            const fy = (dy / dist) * force * this.alpha;

            if (e.sourceNode !== this.draggedNode) { e.sourceNode.x += fx; e.sourceNode.y += fy; }
            if (e.targetNode !== this.draggedNode) { e.targetNode.x -= fx; e.targetNode.y -= fy; }
        }
    }

    draw() {
        if (!this.ctx || !this.canvas) return;
        const width = this.canvas.width / window.devicePixelRatio;
        const height = this.canvas.height / window.devicePixelRatio;

        this.ctx.clearRect(0, 0, width, height);
        this.ctx.save();
        this.ctx.translate(this.transform.x, this.transform.y);
        this.ctx.scale(this.transform.scale, this.transform.scale);

        // Draw Edges
        for (const e of this.edges) {
            this.ctx.beginPath();
            this.ctx.moveTo(e.sourceNode.x, e.sourceNode.y);
            this.ctx.lineTo(e.targetNode.x, e.targetNode.y);
            this.ctx.strokeStyle = "rgba(255, 255, 255, 0.12)";
            this.ctx.lineWidth = 1;
            this.ctx.stroke();
        }

        // Draw Nodes
        for (const n of this.nodes) {
            const isSelected = this.selectedNode === n;
            const isHovered = this.hoveredNode === n;

            // Glow for selected
            if (isSelected || isHovered) {
                this.ctx.beginPath();
                this.ctx.arc(n.x, n.y, n.radius + 6, 0, 2 * Math.PI);
                this.ctx.fillStyle = "rgba(59, 130, 246, 0.35)";
                this.ctx.fill();
            }

            // Node Circle
            this.ctx.beginPath();
            this.ctx.arc(n.x, n.y, n.radius, 0, 2 * Math.PI);
            this.ctx.fillStyle = n.color;
            this.ctx.fill();
            this.ctx.strokeStyle = isSelected ? "#ffffff" : "rgba(0,0,0,0.5)";
            this.ctx.lineWidth = isSelected ? 2 : 1;
            this.ctx.stroke();

            // Label
            this.ctx.font = "10px Inter, sans-serif";
            this.ctx.fillStyle = "#e2e8f0";
            this.ctx.textAlign = "center";
            this.ctx.fillText(n.name, n.x, n.y + n.radius + 12);
        }

        this.ctx.restore();
    }
}

function max(a, b) { return a > b ? a : b; }
