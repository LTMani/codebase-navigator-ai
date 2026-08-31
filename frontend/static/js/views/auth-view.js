import { api } from "../api.js";
import { ToastManager } from "../components/toast.js";
import { store } from "../store.js";

export class AuthView {
    constructor() {
        this.isLoginMode = true;
    }

    render(container) {
        container.innerHTML = `
            <div class="flex items-center justify-center w-full" style="min-height: calc(100vh - 120px);">
                <div class="card" style="width: 100%; max-width: 420px; padding: 32px;">
                    <div class="text-center" style="margin-bottom: 24px;">
                        <h2 style="font-size: 20px; font-weight: 700; margin-bottom: 6px;">
                            ${this.isLoginMode ? "Welcome Back" : "Create Account"}
                        </h2>
                        <p class="text-secondary text-xs">
                            ${this.isLoginMode ? "Sign in to access your indexed codebases" : "Register to analyze and navigate software projects"}
                        </p>
                    </div>

                    <form id="auth-form" class="flex flex-col gap-3">
                        ${!this.isLoginMode ? `
                            <div class="input-group">
                                <label class="input-label">Email Address</label>
                                <input type="email" id="auth-email" class="input-field" placeholder="dev@example.com" required />
                            </div>
                        ` : ''}

                        <div class="input-group">
                            <label class="input-label">Username</label>
                            <input type="text" id="auth-username" class="input-field" placeholder="username" required />
                        </div>

                        <div class="input-group">
                            <label class="input-label">Password</label>
                            <input type="password" id="auth-password" class="input-field" placeholder="••••••••" required />
                        </div>

                        <button type="submit" class="btn btn-primary w-full" style="margin-top: 8px;">
                            ${this.isLoginMode ? "Sign In" : "Register"}
                        </button>
                    </form>

                    <div class="text-center" style="margin-top: 20px;">
                        <button id="toggle-auth-mode" class="text-xs text-accent" style="cursor: pointer;">
                            ${this.isLoginMode ? "Don't have an account? Register" : "Already have an account? Sign In"}
                        </button>
                    </div>
                </div>
            </div>
        `;

        container.querySelector("#toggle-auth-mode")?.addEventListener("click", () => {
            this.isLoginMode = !this.isLoginMode;
            this.render(container);
        });

        container.querySelector("#auth-form")?.addEventListener("submit", async (e) => {
            e.preventDefault();
            const username = container.querySelector("#auth-username")?.value.trim();
            const password = container.querySelector("#auth-password")?.value;
            const email = container.querySelector("#auth-email")?.value.trim();

            try {
                let res;
                if (this.isLoginMode) {
                    res = await api.login({ username, password });
                    ToastManager.success("Signed in successfully!");
                } else {
                    res = await api.register({ username, email, password });
                    ToastManager.success("Account created successfully!");
                }

                if (res.data?.token) {
                    api.setToken(res.data.token);
                    store.setCurrentUser(res.data.user);
                    window.location.hash = "#/dashboard";
                }
            } catch (err) {
                ToastManager.error(err.message || "Authentication failed.");
            }
        });
    }
}
