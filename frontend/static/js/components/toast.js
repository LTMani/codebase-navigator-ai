export class ToastManager {
    static show(message, type = "info", duration = 4000) {
        const container = document.getElementById("toast-container");
        if (!container) return;

        const icons = {
            success: "✅",
            error: "❌",
            warning: "⚠️",
            info: "ℹ️",
        };

        const toast = document.createElement("div");
        toast.className = `toast toast-${type}`;
        toast.innerHTML = `
            <span style="font-size: 16px;">${icons[type] || "ℹ️"}</span>
            <div style="flex: 1; font-size: 13px; line-height: 1.4;">${message}</div>
            <button style="color: var(--text-muted); padding: 4px;" title="Dismiss">&times;</button>
        `;

        const closeBtn = toast.querySelector("button");
        closeBtn.addEventListener("click", () => toast.remove());

        container.appendChild(toast);

        setTimeout(() => {
            if (toast.parentElement) {
                toast.style.opacity = "0";
                toast.style.transform = "translateY(10px)";
                toast.style.transition = "all 0.3s ease";
                setTimeout(() => toast.remove(), 300);
            }
        }, duration);
    }

    static success(msg) { this.show(msg, "success"); }
    static error(msg) { this.show(msg, "error", 6000); }
    static warning(msg) { this.show(msg, "warning", 5000); }
    static info(msg) { this.show(msg, "info"); }
}
