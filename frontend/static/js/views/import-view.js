import { api } from "../api.js";
import { ToastManager } from "../components/toast.js";
import { store } from "../store.js";

export class ImportView {
    render(container) {
        container.innerHTML = `
            <div class="flex items-center justify-center w-full" style="padding: 20px 0;">
                <div class="card flex flex-col gap-6" style="width: 100%; max-width: 620px;">
                    <div>
                        <h2 style="font-size: 20px; font-weight: 700; margin-bottom: 4px;">Import Codebase Project</h2>
                        <p class="text-secondary text-xs">
                            Upload a project archive (ZIP / TAR.GZ) or initialize a repository metadata profile for scanning.
                        </p>
                    </div>

                    <form id="import-form" class="flex flex-col gap-4">
                        <div class="input-group">
                            <label class="input-label">Project Name</label>
                            <input type="text" id="import-name" class="input-field" placeholder="e.g. My Awesome Microservice" required />
                        </div>

                        <div class="input-group">
                            <label class="input-label">Description (Optional)</label>
                            <textarea id="import-desc" class="input-field" rows="2" placeholder="Brief explanation of this service..."></textarea>
                        </div>

                        <!-- Dropzone Area -->
                        <div class="input-group">
                            <label class="input-label">Source Code Archive (.zip, .tar.gz)</label>
                            <div id="import-dropzone" class="dropzone">
                                <div style="font-size: 32px; margin-bottom: 8px;">📦</div>
                                <div style="font-weight: 600; margin-bottom: 4px;">Click to browse or drag & drop archive here</div>
                                <div class="text-xs text-muted">Supports .zip, .tar.gz, .tgz up to 100MB</div>
                                <input type="file" id="import-file" accept=".zip,.tar.gz,.tgz,.tar" style="display: none;" />
                            </div>
                            <div id="import-file-selected" class="font-mono text-xs text-accent" style="margin-top: 6px; display: none;"></div>
                        </div>

                        <button type="submit" id="btn-start-import" class="btn btn-primary btn-lg" style="margin-top: 8px;">
                            <span>⚡</span>
                            <span>Upload & Run AST Analysis</span>
                        </button>
                    </form>
                </div>
            </div>
        `;

        const dropzone = container.querySelector("#import-dropzone");
        const fileInput = container.querySelector("#import-file");
        const fileSelectedText = container.querySelector("#import-file-selected");
        let selectedFile = null;

        dropzone.addEventListener("click", () => fileInput.click());

        fileInput.addEventListener("change", (e) => {
            if (e.target.files.length > 0) {
                selectedFile = e.target.files[0];
                fileSelectedText.style.display = "block";
                fileSelectedText.textContent = `Selected: ${selectedFile.name} (${(selectedFile.size / (1024 * 1024)).toFixed(2)} MB)`;
            }
        });

        dropzone.addEventListener("dragover", (e) => {
            e.preventDefault();
            dropzone.classList.add("drag-over");
        });

        dropzone.addEventListener("dragleave", () => {
            dropzone.classList.remove("drag-over");
        });

        dropzone.addEventListener("drop", (e) => {
            e.preventDefault();
            dropzone.classList.remove("drag-over");
            if (e.dataTransfer.files.length > 0) {
                selectedFile = e.dataTransfer.files[0];
                fileSelectedText.style.display = "block";
                fileSelectedText.textContent = `Selected: ${selectedFile.name} (${(selectedFile.size / (1024 * 1024)).toFixed(2)} MB)`;
            }
        });

        container.querySelector("#import-form").addEventListener("submit", async (e) => {
            e.preventDefault();
            const name = container.querySelector("#import-name").value.trim();
            const description = container.querySelector("#import-desc").value.trim();
            const submitBtn = container.querySelector("#btn-start-import");

            try {
                submitBtn.disabled = true;
                submitBtn.innerHTML = `<span>⏳</span><span>Creating project...</span>`;

                // 1. Create Project
                const projRes = await api.createProject({ name, description });
                const project = projRes.data.project;

                // 2. Upload archive if provided
                if (selectedFile) {
                    submitBtn.innerHTML = `<span>⏳</span><span>Uploading & extracting archive...</span>`;
                    const formData = new FormData();
                    formData.append("file", selectedFile);
                    await api.uploadArchive(project.id, formData);
                }

                // 3. Trigger AST Scanner
                submitBtn.innerHTML = `<span>⏳</span><span>Parsing AST & building dependency graphs...</span>`;
                const scanRes = await api.scanProject(project.id);

                ToastManager.success(`Project '${name}' analyzed successfully! (${scanRes.data?.files_indexed || 0} files)`);
                store.setActiveProject(scanRes.data?.project || project);

                window.location.hash = "#/dashboard";
            } catch (err) {
                ToastManager.error(err.message || "Failed to import project.");
                submitBtn.disabled = false;
                submitBtn.innerHTML = `<span>⚡</span><span>Upload & Run AST Analysis</span>`;
            }
        });
    }
}
