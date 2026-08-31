export class LandingView {
    render(container) {
        container.innerHTML = `
            <div class="fullscreen-view flex flex-col items-center">
                <!-- Hero Section -->
                <section class="hero-section w-full">
                    <div class="badge" style="background: rgba(59,130,246,0.15); color: var(--accent-cyan); margin-bottom: 20px; font-size: 12px; padding: 6px 16px;">
                        ✨ AI-Powered Code Intelligence Platform
                    </div>
                    <h1 class="hero-tagline">
                        Understand Any Codebase.<br/>Navigate with Intelligence.
                    </h1>
                    <p class="hero-subtitle">
                        Instantly map architectures, analyze AST structures, trace execution flows, and simulate change blast radius for unfamiliar software projects.
                    </p>
                    <div class="flex items-center gap-4">
                        <a href="#/import" class="btn btn-primary btn-lg">
                            <span>🚀</span>
                            <span>Import Codebase</span>
                        </a>
                        <a href="#/dashboard" class="btn btn-secondary btn-lg">
                            <span>📊</span>
                            <span>Explore Dashboard</span>
                        </a>
                    </div>
                </section>

                <!-- Core Capability Cards -->
                <section class="feature-grid">
                    <div class="card flex flex-col gap-3">
                        <div style="font-size: 28px;">🏗️</div>
                        <h3 style="font-size: 16px; font-weight: 600;">Layered Architecture Classification</h3>
                        <p class="text-secondary text-sm">
                            Automatically categorizes code into 6 architectural tiers (Presentation, API, Service, Domain, Repository, Infrastructure) and detects boundary violations.
                        </p>
                    </div>

                    <div class="card flex flex-col gap-3">
                        <div style="font-size: 28px;">🕸️</div>
                        <h3 style="font-size: 16px; font-weight: 600;">Dependency Graph & Tarjan Cycles</h3>
                        <p class="text-secondary text-sm">
                            High-performance Canvas graph engine detecting circular dependency clusters with Tarjan's SCC and computing PageRank importance scores.
                        </p>
                    </div>

                    <div class="card flex flex-col gap-3">
                        <div style="font-size: 28px;">💥</div>
                        <h3 style="font-size: 16px; font-weight: 600;">Change Blast Radius Simulator</h3>
                        <p class="text-secondary text-sm">
                            Predicts upstream and downstream impact before you edit code, flagging affected routes, models, and test suites.
                        </p>
                    </div>

                    <div class="card flex flex-col gap-3">
                        <div style="font-size: 28px;">🩺</div>
                        <h3 style="font-size: 16px; font-weight: 600;">Code Health & Technical Debt</h3>
                        <p class="text-secondary text-sm">
                            Calculates Halstead Volume, McCabe Cyclomatic Complexity, Maintainability Index, and estimated refactoring hours.
                        </p>
                    </div>

                    <div class="card flex flex-col gap-3">
                        <div style="font-size: 28px;">🧭</div>
                        <h3 style="font-size: 16px; font-weight: 600;">Developer Onboarding Tour</h3>
                        <p class="text-secondary text-sm">
                            Auto-generates curated reading paths, domain concept guides, and interactive knowledge checks for new engineers.
                        </p>
                    </div>

                    <div class="card flex flex-col gap-3">
                        <div style="font-size: 28px;">🤖</div>
                        <h3 style="font-size: 16px; font-weight: 600;">Grounded AI Codebase Copilot</h3>
                        <p class="text-secondary text-sm">
                            Dual-mode assistant providing citation-backed answers grounded strictly in extracted AST symbols and dependency graphs.
                        </p>
                    </div>
                </section>
            </div>
        `;
    }
}
