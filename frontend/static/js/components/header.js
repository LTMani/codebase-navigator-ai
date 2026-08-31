import { eventBus } from "../event-bus.js";
import { store } from "../store.js";

export class HeaderComponent {
    static init() {
        const toggleBtn = document.getElementById("btn-toggle-sidebar");
        const breadcrumbs = document.getElementById("header-breadcrumbs");
        const statusBadge = document.getElementById("header-status-badge");
        const userMenu = document.getElementById("header-user-menu");

        toggleBtn?.addEventListener("click", () => {
            store.toggleSidebar();
        });

        eventBus.on("route:changed", ({ path }) => {
            const cleanPath = path.replace("#/", "").replace("/", " > ");
            if (breadcrumbs) {
                const formatted = cleanPath ? cleanPath.charAt(0).toUpperCase() + cleanPath.slice(1) : "Dashboard";
                breadcrumbs.innerHTML = `<span>CodeBase Navigator</span> <span>/</span> <span style="color: var(--text-primary); font-weight: 600;">${formatted}</span>`;
            }
        });

        eventBus.on("project:selected", (project) => {
            if (statusBadge && project) {
                const statusColors = {
                    analyzed: "var(--accent-emerald)",
                    scanning: "var(--accent-primary)",
                    pending: "var(--accent-amber)",
                    failed: "var(--accent-rose)",
                };
                const color = statusColors[project.status] || "var(--text-muted)";
                statusBadge.innerHTML = `
                    <div class="flex items-center gap-2" style="background: rgba(255,255,255,0.05); padding: 4px 10px; border-radius: var(--radius-full); font-size: 11px;">
                        <span style="width: 8px; height: 8px; border-radius: 50%; background: ${color};"></span>
                        <span style="font-weight: 600; color: var(--text-secondary);">${project.name}</span>
                        <span class="badge" style="font-size: 10px; background: rgba(59,130,246,0.15); color: var(--accent-cyan);">${project.version}</span>
                    </div>
                `;
            }
        });

        eventBus.on("auth:changed", ({ user, isAuthenticated }) => {
            if (userMenu) {
                if (isAuthenticated && user) {
                    userMenu.innerHTML = `
                        <div class="flex items-center gap-2">
                            <div style="width: 30px; height: 30px; border-radius: 50%; background: var(--bg-tertiary); border: 1px solid var(--border-color); display: flex; align-items: center; justify-content: center; font-weight: 600; font-size: 12px; color: var(--accent-cyan);">
                                ${user.username.substring(0, 2).toUpperCase()}
                            </div>
                        </div>
                    `;
                } else {
                    userMenu.innerHTML = `<a href="#/auth" class="btn btn-primary btn-sm">Sign In</a>`;
                }
            }
        });
    }
}
