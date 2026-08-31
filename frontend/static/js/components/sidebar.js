import { api } from "../api.js";
import { eventBus } from "../event-bus.js";
import { store } from "../store.js";

export class SidebarComponent {
    static init() {
        const sidebar = document.getElementById("app-sidebar");
        const navContainer = document.getElementById("sidebar-nav-links");
        const projectSelector = document.getElementById("project-selector-container");
        const userFooter = document.getElementById("sidebar-user-footer");

        eventBus.on("sidebar:toggled", (isCollapsed) => {
            sidebar?.classList.toggle("collapsed", isCollapsed);
        });

        eventBus.on("projects:updated", (projects) => {
            this.renderProjectSelector(projectSelector, projects);
        });

        eventBus.on("project:selected", (project) => {
            this.renderNavLinks(navContainer, project);
        });

        eventBus.on("auth:changed", ({ user, isAuthenticated }) => {
            this.renderUserFooter(userFooter, user, isAuthenticated);
        });

        eventBus.on("route:changed", ({ path }) => {
            navContainer?.querySelectorAll("a").forEach((a) => {
                const targetHash = a.getAttribute("href");
                if (targetHash === path) {
                    a.style.backgroundColor = "var(--bg-active)";
                    a.style.color = "var(--accent-cyan)";
                } else {
                    a.style.backgroundColor = "transparent";
                    a.style.color = "var(--text-secondary)";
                }
            });
        });
    }

    static renderProjectSelector(container, projects) {
        if (!container) return;
        const activeProj = store.getState().activeProject;

        if (!projects || projects.length === 0) {
            container.innerHTML = `
                <a href="#/import" class="btn btn-primary btn-sm w-full flex items-center justify-center gap-2">
                    <span>➕</span>
                    <span>Import Codebase</span>
                </a>
            `;
            return;
        }

        container.innerHTML = `
            <div class="flex flex-col gap-1">
                <label class="text-xs text-muted" style="font-weight: 500;">ACTIVE PROJECT</label>
                <select id="sidebar-project-select" class="input-field font-bold text-sm" style="padding: 6px 10px; background: var(--bg-tertiary);">
                    ${projects.map(p => `
                        <option value="${p.id}" ${activeProj?.id === p.id ? "selected" : ""}>
                            ${p.name} (${p.file_count} files)
                        </option>
                    `).join("")}
                </select>
            </div>
        `;

        container.querySelector("#sidebar-project-select")?.addEventListener("change", (e) => {
            const selected = projects.find(p => p.id === e.target.value);
            if (selected) {
                store.setActiveProject(selected);
            }
        });
    }

    static renderNavLinks(container, activeProject) {
        if (!container) return;

        const currentHash = window.location.hash || "#/dashboard";

        const navGroups = [
            {
                title: "EXPLORATION & WORKSPACE",
                items: [
                    { icon: "📊", label: "Dashboard", hash: "#/dashboard" },
                    { icon: "💻", label: "Workspace & Editor", hash: "#/workspace" },
                    { icon: "📁", label: "Structure Explorer", hash: "#/structure" },
                    { icon: "🔍", label: "Code Search", hash: "#/search" },
                ],
            },
            {
                title: "CODE INTELLIGENCE",
                items: [
                    { icon: "🏗️", label: "Architecture Layers", hash: "#/architecture" },
                    { icon: "🕸️", label: "Dependency Graph", hash: "#/dependencies" },
                    { icon: "🔁", label: "Circular Dependencies", hash: "#/circular" },
                    { icon: "⚡", label: "Code Flow Explorer", hash: "#/flows" },
                    { icon: "💥", label: "Change Impact Simulator", hash: "#/impact" },
                ],
            },
            {
                title: "QUALITY & ONBOARDING",
                items: [
                    { icon: "🩺", label: "Code Health & Hotspots", hash: "#/health" },
                    { icon: "🧭", label: "Developer Onboarding", hash: "#/onboarding" },
                    { icon: "🗺️", label: "Knowledge Map", hash: "#/knowledge-map" },
                    { icon: "🤖", label: "AI Codebase Copilot", hash: "#/copilot" },
                    { icon: "📄", label: "Audit Reports", hash: "#/reports" },
                    { icon: "⏱️", label: "Analysis History", hash: "#/history" },
                ],
            },
            {
                title: "MANAGEMENT",
                items: [
                    { icon: "📥", label: "Import Project", hash: "#/import" },
                    { icon: "⚙️", label: "System Settings", hash: "#/settings" },
                ],
            },
        ];

        let html = "";
        for (const group of navGroups) {
            html += `<div style="font-size: 10px; font-weight: 700; color: var(--text-dim); padding: 10px 12px 4px; letter-spacing: 0.05em;">${group.title}</div>`;
            for (const item of group.items) {
                const isActive = currentHash.startsWith(item.hash);
                html += `
                    <a href="${item.hash}" class="flex items-center gap-3" style="padding: 8px 12px; border-radius: var(--radius-sm); font-size: 13px; font-weight: 500; color: ${isActive ? "var(--accent-cyan)" : "var(--text-secondary)"}; background: ${isActive ? "var(--bg-active)" : "transparent"}; transition: all var(--transition-fast);">
                        <span style="font-size: 15px;">${item.icon}</span>
                        <span class="truncate">${item.label}</span>
                    </a>
                `;
            }
        }

        container.innerHTML = html;
    }

    static renderUserFooter(container, user, isAuthenticated) {
        if (!container) return;

        if (isAuthenticated && user) {
            container.innerHTML = `
                <div class="flex items-center gap-2 truncate">
                    <div style="width: 28px; height: 28px; border-radius: 50%; background: var(--bg-tertiary); display: flex; align-items: center; justify-content: center; font-size: 11px; font-weight: 700; color: var(--accent-primary);">
                        ${user.username[0].toUpperCase()}
                    </div>
                    <div class="flex flex-col truncate">
                        <span class="text-sm font-bold truncate">${user.username}</span>
                        <span class="text-xs text-muted truncate">${user.email}</span>
                    </div>
                </div>
                <button id="btn-signout" class="btn btn-outline btn-sm" title="Sign Out">🚪</button>
            `;

            container.querySelector("#btn-signout")?.addEventListener("click", () => {
                api.setToken(null);
                store.setCurrentUser(null);
                window.location.hash = "#/auth";
            });
        } else {
            container.innerHTML = `
                <a href="#/auth" class="btn btn-primary btn-sm w-full text-center">Sign In / Register</a>
            `;
        }
    }
}
