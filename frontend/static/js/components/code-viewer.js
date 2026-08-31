export class CodeViewerComponent {
    constructor(container) {
        this.container = container;
        this.currentCode = "";
        this.currentFilePath = "";
    }

    render(filePath, codeContent, targetLine = null) {
        if (!this.container) return;
        this.currentFilePath = filePath;
        this.currentCode = codeContent || "";

        const lines = this.currentCode.split("\n");
        const lineCount = lines.length;

        this.container.innerHTML = `
            <div class="code-viewer-container">
                <div class="code-viewer-header">
                    <div class="flex items-center gap-2 font-mono text-xs truncate">
                        <span>📄</span>
                        <span style="color: var(--text-primary); font-weight: 600;">${filePath || "No file selected"}</span>
                        <span class="text-muted">(${lineCount} lines)</span>
                    </div>
                    <div class="flex items-center gap-2">
                        <button id="btn-copy-code" class="btn btn-secondary btn-sm" title="Copy code to clipboard">📋 Copy</button>
                    </div>
                </div>
                <div class="code-viewer-body" id="code-body-scroll">
                    <div class="line-numbers font-mono text-xs">
                        ${Array.from({ length: lineCount }, (_, i) => `<div class="line-num" data-line="${i + 1}">${i + 1}</div>`).join("")}
                    </div>
                    <div class="code-lines-content font-mono text-xs">
                        ${lines.map((line, idx) => `
                            <div class="code-line ${targetLine === idx + 1 ? 'active-line' : ''}" data-line="${idx + 1}" style="${targetLine === idx + 1 ? 'background: rgba(59,130,246,0.2); border-left: 2px solid var(--accent-primary);' : ''}">
                                ${this.highlightSyntax(line, filePath)}
                            </div>
                        `).join("")}
                    </div>
                </div>
            </div>
        `;

        this.container.querySelector("#btn-copy-code")?.addEventListener("click", () => {
            navigator.clipboard.writeText(this.currentCode);
            alert("Code copied to clipboard!");
        });

        if (targetLine && targetLine > 0) {
            setTimeout(() => {
                const lineEl = this.container.querySelector(`.code-line[data-line="${targetLine}"]`);
                lineEl?.scrollIntoView({ behavior: "smooth", block: "center" });
            }, 100);
        }
    }

    highlightSyntax(rawLine, filePath) {
        if (!rawLine) return "&nbsp;";

        let escaped = rawLine
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;");

        // Basic universal syntax highlighting rules
        // Comments
        if (escaped.trim().startsWith("#") || escaped.trim().startsWith("//")) {
            return `<span class="token-comment">${escaped}</span>`;
        }

        // Keywords
        const keywords = ["def ", "class ", "return ", "import ", "from ", "if ", "else:", "elif ", "for ", "while ", "try:", "except ", "const ", "let ", "var ", "function ", "async ", "await ", "export ", "default "];
        for (const kw of keywords) {
            if (escaped.includes(kw)) {
                escaped = escaped.replace(new RegExp(`\\b${kw.trim()}\\b`, 'g'), `<span class="token-keyword">${kw.trim()}</span>`);
            }
        }

        // Decorators
        if (escaped.trim().startsWith("@")) {
            escaped = `<span class="token-decorator">${escaped}</span>`;
        }

        return escaped;
    }
}
