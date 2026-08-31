import { api } from "../api.js";
import { ToastManager } from "../components/toast.js";
import { store } from "../store.js";

export class CopilotView {
    async render(container) {
        const activeProj = store.getState().activeProject;
        if (!activeProj) {
            container.innerHTML = `<div class="card text-center">Please select a project first.</div>`;
            return;
        }

        container.innerHTML = `
            <div class="chat-container">
                <!-- Chat Header -->
                <div class="flex items-center justify-between" style="padding: 16px 20px; border-bottom: 1px solid var(--border-color); background: rgba(0,0,0,0.15);">
                    <div class="flex items-center gap-3">
                        <div style="width: 32px; height: 32px; border-radius: 8px; background: linear-gradient(135deg, #8b5cf6, #3b82f6); display: flex; align-items: center; justify-content: center; font-size: 16px;">
                            🤖
                        </div>
                        <div>
                            <h3 style="font-size: 15px; font-weight: 700;">AI Codebase Copilot</h3>
                            <span class="text-xs text-muted">Grounded in AST intelligence and dependency graphs</span>
                        </div>
                    </div>
                </div>

                <!-- Chat Messages Scroll Area -->
                <div id="copilot-messages" class="chat-messages-area">
                    <div class="chat-bubble assistant">
                        Hello! I am your AI Codebase Copilot for <strong>${activeProj.name}</strong>. Ask me anything about the architecture, execution flows, authentication lifecycle, or what happens if you modify a particular file.
                    </div>
                </div>

                <!-- Chat Input Area -->
                <div style="padding: 16px 20px; border-top: 1px solid var(--border-color); background: var(--bg-tertiary);">
                    <form id="copilot-form" class="flex items-center gap-3">
                        <input type="text" id="copilot-input" class="input-field" placeholder="Ask about architecture, flows, blast radius, or files..." autocomplete="off" />
                        <button type="submit" id="btn-send-copilot" class="btn btn-primary" style="padding: 10px 20px;">
                            <span>Send</span>
                        </button>
                    </form>
                </div>
            </div>
        `;

        const form = container.querySelector("#copilot-form");
        const input = container.querySelector("#copilot-input");
        const messagesContainer = container.querySelector("#copilot-messages");
        const sendBtn = container.querySelector("#btn-send-copilot");

        form.addEventListener("submit", async (e) => {
            e.preventDefault();
            const prompt = input.value.trim();
            if (!prompt) return;

            // 1. Append User Message Bubble
            const userBubble = document.createElement("div");
            userBubble.className = "chat-bubble user";
            userBubble.textContent = prompt;
            messagesContainer.appendChild(userBubble);
            input.value = "";
            messagesContainer.scrollTop = messagesContainer.scrollHeight;

            // 2. Append Thinking Bubble
            const thinkingBubble = document.createElement("div");
            thinkingBubble.className = "chat-bubble assistant animate-pulse-glow";
            thinkingBubble.textContent = "Analyzing AST intelligence and assembling citations...";
            messagesContainer.appendChild(thinkingBubble);
            messagesContainer.scrollTop = messagesContainer.scrollHeight;

            try {
                sendBtn.disabled = true;
                const res = await api.queryCopilot(activeProj.id, { prompt });
                const assistantData = res.data;

                thinkingBubble.classList.remove("animate-pulse-glow");
                thinkingBubble.innerHTML = `
                    <div class="markdown-body text-sm" style="line-height: 1.6;">
                        ${this.formatMarkdown(assistantData.content)}
                    </div>
                    ${assistantData.citations?.length ? `
                        <div style="margin-top: 12px; padding-top: 8px; border-top: 1px solid rgba(255,255,255,0.06);">
                            <span class="text-xs font-bold text-muted">CITATIONS:</span>
                            <div class="flex flex-wrap gap-1" style="margin-top: 4px;">
                                ${assistantData.citations.map(c => `
                                    <span class="badge" style="background: rgba(59,130,246,0.15); color: var(--accent-cyan); font-size: 10px;">
                                        📄 ${c.file_path}:${c.line}
                                    </span>
                                `).join("")}
                            </div>
                        </div>
                    ` : ''}
                `;
            } catch (err) {
                thinkingBubble.classList.remove("animate-pulse-glow");
                thinkingBubble.textContent = `Error: ${err.message || "Failed to query Copilot."}`;
            } finally {
                sendBtn.disabled = false;
                messagesContainer.scrollTop = messagesContainer.scrollHeight;
            }
        });
    }

    formatMarkdown(text) {
        if (!text) return "";
        return text
            .replace(/### (.*?)\n/g, '<h4 style="font-weight: 700; margin: 8px 0 4px; font-size: 14px;">$1</h4>')
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/`([^`]+)`/g, '<code style="background: rgba(255,255,255,0.1); padding: 2px 4px; border-radius: 4px; font-family: var(--font-mono); font-size: 12px;">$1</code>')
            .replace(/\n\n/g, '<br/><br/>')
            .replace(/\n- /g, '<br/>• ');
    }
}
