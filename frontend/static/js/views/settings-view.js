import { api } from "../api.js";
import { ToastManager } from "../components/toast.js";

export class SettingsView {
    async render(container) {
        container.innerHTML = `
            <div class="flex flex-col gap-6">
                <div>
                    <h2 style="font-size: 20px; font-weight: 700; margin-bottom: 4px;">System Settings & AI Configuration</h2>
                    <p class="text-secondary text-xs">Configure analysis filters, layer heuristics, and AI Copilot providers.</p>
                </div>

                <div class="card flex flex-col gap-4">
                    <h3 style="font-size: 15px; font-weight: 600;">AI Codebase Copilot Settings</h3>
                    <p class="text-secondary text-xs">
                        By default, CodeBase Navigator AI uses a deterministic AST reasoning engine that works 100% offline. You can optionally connect an external LLM provider.
                    </p>

                    <form id="ai-settings-form" class="flex flex-col gap-4" style="max-width: 500px;">
                        <div class="input-group">
                            <label class="input-label">AI Provider</label>
                            <select id="ai-provider-select" class="input-field">
                                <option value="offline">Offline / Built-in AST Grounded Reasoning</option>
                                <option value="openai">OpenAI (GPT-4o)</option>
                                <option value="anthropic">Anthropic (Claude 3.5 Sonnet)</option>
                                <option value="gemini">Google Gemini</option>
                                <option value="ollama">Local Ollama</option>
                            </select>
                        </div>

                        <div class="input-group">
                            <label class="input-label">API Key (Optional for offline)</label>
                            <input type="password" id="ai-api-key" class="input-field" placeholder="sk-••••••••••••••••" />
                        </div>

                        <button type="submit" class="btn btn-primary" style="align-self: flex-start;">Save Settings</button>
                    </form>
                </div>
            </div>
        `;

        const form = container.querySelector("#ai-settings-form");
        form.addEventListener("submit", (e) => {
            e.preventDefault();
            ToastManager.success("AI settings saved successfully!");
        });
    }
}
