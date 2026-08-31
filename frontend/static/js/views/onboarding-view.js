import { api } from "../api.js";
import { ToastManager } from "../components/toast.js";
import { store } from "../store.js";

export class OnboardingView {
    async render(container) {
        const activeProj = store.getState().activeProject;
        if (!activeProj) {
            container.innerHTML = `<div class="card text-center">Please select a project first.</div>`;
            return;
        }

        container.innerHTML = `
            <div class="flex items-center justify-center h-full text-secondary">
                Generating developer onboarding journey...
            </div>
        `;

        try {
            const res = await api.getOnboardingPlan(activeProj.id);
            this.renderPlan(container, res.data, activeProj);
        } catch (err) {
            ToastManager.error("Failed to generate onboarding plan.");
        }
    }

    renderPlan(container, plan, project) {
        const readingPath = plan.reading_path || [];
        const coreConcepts = plan.core_concepts || [];
        const quiz = plan.knowledge_check || [];

        container.innerHTML = `
            <div class="flex flex-col gap-6">
                <!-- Header Banner -->
                <div class="card flex flex-col gap-2" style="background: linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.9) 100%);">
                    <div class="flex items-center justify-between">
                        <h2 style="font-size: 20px; font-weight: 700;">${plan.title}</h2>
                        <span class="badge badge-layer-service">⏱️ ~${plan.estimated_read_time_minutes} Min Reading Tour</span>
                    </div>
                    <p class="text-secondary text-sm">${plan.executive_summary}</p>
                </div>

                <!-- 1. Suggested Reading Path -->
                <div class="card flex flex-col gap-4">
                    <h3 style="font-size: 16px; font-weight: 600;">1. Prioritized Reading Order</h3>
                    <p class="text-secondary text-xs">Recommended order of files to read based on entry points and PageRank centrality.</p>
                    <div class="flex flex-col gap-2">
                        ${readingPath.map(r => `
                            <div class="flex items-center justify-between font-mono text-xs" style="padding: 10px 14px; background: var(--bg-tertiary); border-radius: var(--radius-sm);">
                                <div class="flex items-center gap-3">
                                    <span style="font-weight: 800; color: var(--accent-primary); font-size: 14px;">#${r.order}</span>
                                    <div class="flex flex-col">
                                        <span style="font-weight: 700; color: var(--text-primary); font-size: 13px;">${r.file_path}</span>
                                        <span class="text-muted text-xs">${r.reason}</span>
                                    </div>
                                </div>
                                <div class="flex items-center gap-3">
                                    <span class="badge badge-layer-${r.layer}">${r.layer}</span>
                                    <button class="btn btn-outline btn-sm open-file-btn" data-path="${r.file_path}">Read File</button>
                                </div>
                            </div>
                        `).join("")}
                    </div>
                </div>

                <!-- 2. Core Domain Concepts -->
                ${coreConcepts.length > 0 ? `
                    <div class="card flex flex-col gap-4">
                        <h3 style="font-size: 16px; font-weight: 600;">2. Core Domain Concepts & Entities</h3>
                        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 14px;">
                            ${coreConcepts.map(c => `
                                <div class="card flex flex-col gap-1" style="background: var(--bg-tertiary); padding: 12px;">
                                    <div class="flex items-center justify-between font-mono text-xs">
                                        <span style="font-weight: 700; color: var(--accent-amber);">🔷 ${c.name}</span>
                                        <span class="text-muted">${c.methods_count} methods</span>
                                    </div>
                                    <p class="text-xs text-secondary" style="margin-top: 4px;">${c.docstring}</p>
                                </div>
                            `).join("")}
                        </div>
                    </div>
                ` : ''}

                <!-- 3. Interactive Knowledge Check (Quiz) -->
                ${quiz.length > 0 ? `
                    <div class="card flex flex-col gap-4">
                        <h3 style="font-size: 16px; font-weight: 600;">3. Interactive Knowledge Check</h3>
                        <p class="text-secondary text-xs">Test your comprehension of this codebase's architecture and entry points.</p>

                        <form id="onboarding-quiz-form" class="flex flex-col gap-6" style="margin-top: 8px;">
                            ${quiz.map((q, qIndex) => `
                                <div class="card flex flex-col gap-3" style="background: var(--bg-tertiary); padding: 16px;">
                                    <div style="font-weight: 600; font-size: 13px;">${qIndex + 1}. ${q.question}</div>
                                    <div class="flex flex-col gap-2 font-mono text-xs">
                                        ${q.options.map((opt, optIndex) => `
                                            <label class="flex items-center gap-2" style="cursor: pointer;">
                                                <input type="radio" name="${q.id}" value="${opt}" required />
                                                <span>${opt}</span>
                                            </label>
                                        `).join("")}
                                    </div>
                                </div>
                            `).join("")}

                            <button type="submit" id="btn-submit-quiz" class="btn btn-primary" style="align-self: flex-start;">
                                Submit Knowledge Check
                            </button>
                        </form>

                        <div id="quiz-results-banner"></div>
                    </div>
                ` : ''}
            </div>
        `;

        container.querySelectorAll(".open-file-btn").forEach(btn => {
            btn.addEventListener("click", () => {
                const path = btn.getAttribute("data-path");
                store.setActiveFile({ path });
                window.location.hash = "#/workspace";
            });
        });

        const quizForm = container.querySelector("#onboarding-quiz-form");
        quizForm?.addEventListener("submit", async (e) => {
            e.preventDefault();
            const formData = new FormData(quizForm);
            const answers = {};
            for (const [k, v] of formData.entries()) {
                answers[k] = v;
            }

            try {
                const res = await api.submitQuiz(project.id, answers);
                const score = res.data.score_percent;
                const banner = container.querySelector("#quiz-results-banner");
                banner.innerHTML = `
                    <div class="card flex items-center justify-between" style="border-left: 4px solid ${res.data.passed ? 'var(--accent-emerald)' : 'var(--accent-amber)'}; margin-top: 16px;">
                        <div>
                            <h4 style="font-size: 16px; font-weight: 700;">Score: ${score}% (${res.data.correct_count}/${res.data.total_questions} Correct)</h4>
                            <p class="text-xs text-secondary">${res.data.passed ? '🎉 Congratulations! You have a solid grasp of this codebase structure.' : 'Keep exploring the files and retry!'}</p>
                        </div>
                    </div>
                `;
            } catch (err) {
                ToastManager.error("Failed to evaluate quiz.");
            }
        });
    }
}
