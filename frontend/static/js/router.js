import { eventBus } from "./event-bus.js";
import { LandingView } from "./views/landing-view.js";
import { AuthView } from "./views/auth-view.js";
import { DashboardView } from "./views/dashboard-view.js";
import { ImportView } from "./views/import-view.js";
import { WorkspaceView } from "./views/workspace-view.js";
import { StructureView } from "./views/structure-view.js";
import { ArchitectureView } from "./views/architecture-view.js";
import { DependencyView } from "./views/dependency-view.js";
import { FileIntelligenceView } from "./views/file-intelligence-view.js";
import { CodeFlowView } from "./views/code-flow-view.js";
import { ImpactView } from "./views/impact-view.js";
import { SearchView } from "./views/search-view.js";
import { HealthView } from "./views/health-view.js";
import { CircularDependenciesView } from "./views/circular-dependencies-view.js";
import { OnboardingView } from "./views/onboarding-view.js";
import { KnowledgeMapView } from "./views/knowledge-map-view.js";
import { CopilotView } from "./views/copilot-view.js";
import { HistoryView } from "./views/history-view.js";
import { ReportsView } from "./views/reports-view.js";
import { SettingsView } from "./views/settings-view.js";

export class Router {
    constructor(viewContainerId = "view-container") {
        this.container = document.getElementById(viewContainerId);
        this.routes = {
            "#/": new LandingView(),
            "#/auth": new AuthView(),
            "#/dashboard": new DashboardView(),
            "#/import": new ImportView(),
            "#/workspace": new WorkspaceView(),
            "#/structure": new StructureView(),
            "#/architecture": new ArchitectureView(),
            "#/dependencies": new DependencyView(),
            "#/intelligence": new FileIntelligenceView(),
            "#/flows": new CodeFlowView(),
            "#/impact": new ImpactView(),
            "#/search": new SearchView(),
            "#/health": new HealthView(),
            "#/circular": new CircularDependenciesView(),
            "#/onboarding": new OnboardingView(),
            "#/knowledge-map": new KnowledgeMapView(),
            "#/copilot": new CopilotView(),
            "#/history": new HistoryView(),
            "#/reports": new ReportsView(),
            "#/settings": new SettingsView(),
        };

        window.addEventListener("hashchange", () => this.handleRoute());
    }

    init() {
        if (!window.location.hash) {
            window.location.hash = "#/";
        }
        this.handleRoute();
    }

    async handleRoute() {
        const hash = window.location.hash || "#/";
        const view = this.routes[hash] || this.routes["#/dashboard"] || this.routes["#/"];

        if (this.container && view) {
            if (hash === "#/" || hash === "#/landing") {
                this.container.classList.add("fullscreen-view");
            } else {
                this.container.classList.remove("fullscreen-view");
            }

            eventBus.emit("route:changed", { path: hash });
            this.container.innerHTML = "";
            await view.render(this.container);
        }
    }
}
