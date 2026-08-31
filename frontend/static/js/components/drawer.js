export class DrawerManager {
    static open(title, contentHtml) {
        const drawer = document.getElementById("detail-drawer");
        const contentContainer = document.getElementById("detail-drawer-content");
        if (!drawer || !contentContainer) return;

        contentContainer.innerHTML = `
            <div class="flex items-center justify-between" style="padding-bottom: 16px; border-bottom: 1px solid var(--border-color); margin-bottom: 20px;">
                <h3 style="font-size: 16px; font-weight: 600;">${title}</h3>
                <button id="drawer-close-btn" style="color: var(--text-muted); font-size: 20px;">&times;</button>
            </div>
            <div style="overflow-y: auto; height: calc(100% - 60px);">
                ${contentHtml}
            </div>
        `;

        drawer.classList.add("active");

        drawer.querySelector("#drawer-close-btn")?.addEventListener("click", () => {
            drawer.classList.remove("active");
        });

        drawer.addEventListener("click", (e) => {
            if (e.target === drawer) {
                drawer.classList.remove("active");
            }
        });
    }

    static close() {
        const drawer = document.getElementById("detail-drawer");
        if (drawer) drawer.classList.remove("active");
    }
}
