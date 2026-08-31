import { api } from "./api.js";
import { CommandPalette } from "./components/command-palette.js";
import { HeaderComponent } from "./components/header.js";
import { SidebarComponent } from "./components/sidebar.js";
import { Router } from "./router.js";
import { store } from "./store.js";

class Application {
    static async bootstrap() {
        console.log("🚀 Bootstrapping CodeBase Navigator AI Application...");

        // 1. Initialize UI Shell Components
        HeaderComponent.init();
        SidebarComponent.init();
        CommandPalette.init();

        // 2. Authenticate session if token exists
        if (api.getToken()) {
            try {
                const userRes = await api.getCurrentUser();
                store.setCurrentUser(userRes.data?.user);
            } catch (err) {
                console.warn("Session expired or invalid token.");
                api.setToken(null);
            }
        }

        // 3. Load initial projects
        try {
            const projectsRes = await api.getProjects();
            store.setProjects(projectsRes.data?.projects || []);
        } catch (err) {
            console.warn("Could not fetch initial projects.");
        }

        // 4. Initialize Router
        const router = new Router();
        router.init();

        console.log("✅ CodeBase Navigator AI ready.");
    }
}

document.addEventListener("DOMContentLoaded", () => {
    Application.bootstrap();
});
