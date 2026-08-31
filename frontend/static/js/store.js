import { eventBus } from "./event-bus.js";

class StateStore {
    constructor() {
        this.state = {
            currentUser: null,
            isAuthenticated: false,
            projects: [],
            activeProject: null,
            activeFile: null,
            projectTree: null,
            sidebarCollapsed: false,
            theme: "dark",
        };
    }

    getState() {
        return this.state;
    }

    setCurrentUser(user) {
        this.state.currentUser = user;
        this.state.isAuthenticated = !!user;
        eventBus.emit("auth:changed", { user, isAuthenticated: !!user });
    }

    setProjects(projects) {
        this.state.projects = projects || [];
        eventBus.emit("projects:updated", this.state.projects);

        // Auto-select first project if none active
        if (!this.state.activeProject && this.state.projects.length > 0) {
            const savedSlug = localStorage.getItem("cn_active_project_slug");
            const match = this.state.projects.find(p => p.slug === savedSlug) || this.state.projects[0];
            this.setActiveProject(match);
        }
    }

    setActiveProject(project) {
        this.state.activeProject = project;
        if (project?.slug) {
            localStorage.setItem("cn_active_project_slug", project.slug);
        }
        eventBus.emit("project:selected", project);
    }

    setActiveFile(file) {
        this.state.activeFile = file;
        eventBus.emit("file:selected", file);
    }

    setProjectTree(tree) {
        this.state.projectTree = tree;
        eventBus.emit("tree:updated", tree);
    }

    toggleSidebar() {
        this.state.sidebarCollapsed = !this.state.sidebarCollapsed;
        eventBus.emit("sidebar:toggled", this.state.sidebarCollapsed);
    }
}

export const store = new StateStore();
