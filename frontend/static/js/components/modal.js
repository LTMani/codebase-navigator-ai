export class ModalManager {
    static open(title, contentHtml, onConfirm = null, confirmText = "Confirm") {
        let modalOverlay = document.getElementById("generic-modal");
        if (!modalOverlay) {
            modalOverlay = document.createElement("div");
            modalOverlay.id = "generic-modal";
            modalOverlay.className = "modal-overlay";
            document.body.appendChild(modalOverlay);
        }

        modalOverlay.innerHTML = `
            <div class="modal-box">
                <div class="flex items-center justify-between" style="padding: 18px 24px; border-bottom: 1px solid var(--border-color);">
                    <h3 style="font-size: 16px; font-weight: 600;">${title}</h3>
                    <button id="modal-close-btn" style="color: var(--text-muted); font-size: 20px;">&times;</button>
                </div>
                <div style="padding: 24px;">
                    ${contentHtml}
                </div>
                <div class="flex items-center justify-end gap-3" style="padding: 16px 24px; border-top: 1px solid var(--border-color); background: rgba(0,0,0,0.15);">
                    <button id="modal-cancel-btn" class="btn btn-secondary">Cancel</button>
                    ${onConfirm ? `<button id="modal-confirm-btn" class="btn btn-primary">${confirmText}</button>` : ""}
                </div>
            </div>
        `;

        modalOverlay.classList.add("active");

        const close = () => {
            modalOverlay.classList.remove("active");
        };

        modalOverlay.querySelector("#modal-close-btn")?.addEventListener("click", close);
        modalOverlay.querySelector("#modal-cancel-btn")?.addEventListener("click", close);

        const confirmBtn = modalOverlay.querySelector("#modal-confirm-btn");
        if (confirmBtn && onConfirm) {
            confirmBtn.addEventListener("click", async () => {
                const proceed = await onConfirm();
                if (proceed !== false) {
                    close();
                }
            });
        }
    }

    static close() {
        const modal = document.getElementById("generic-modal");
        if (modal) modal.classList.remove("active");
    }
}
