export class MetricsChartComponent {
    static renderLanguageDistribution(container, languages) {
        if (!container || !languages) return;

        const entries = Object.entries(languages);
        const totalFiles = entries.reduce((acc, [_, v]) => acc + (v.files || 0), 0) || 1;

        container.innerHTML = `
            <div class="flex flex-col gap-3">
                <div class="flex w-full" style="height: 10px; border-radius: var(--radius-full); overflow: hidden; background: var(--bg-tertiary);">
                    ${entries.map(([lang, data], i) => {
                        const pct = ((data.files || 0) / totalFiles) * 100;
                        const colors = ["#3b82f6", "#06b6d4", "#10b981", "#8b5cf6", "#f59e0b", "#ec4899"];
                        return `<div style="width: ${pct}%; background: ${colors[i % colors.length]};" title="${lang}: ${pct.toFixed(1)}%"></div>`;
                    }).join("")}
                </div>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 8px;">
                    ${entries.map(([lang, data], i) => {
                        const pct = (((data.files || 0) / totalFiles) * 100).toFixed(1);
                        const colors = ["#3b82f6", "#06b6d4", "#10b981", "#8b5cf6", "#f59e0b", "#ec4899"];
                        return `
                            <div class="flex items-center gap-2 text-xs">
                                <span style="width: 8px; height: 8px; border-radius: 50%; background: ${colors[i % colors.length]};"></span>
                                <span style="font-weight: 600;">${lang}</span>
                                <span class="text-muted">(${pct}%)</span>
                            </div>
                        `;
                    }).join("")}
                </div>
            </div>
        `;
    }

    static renderComplexityBar(container, complexity) {
        const val = Math.min(complexity, 25);
        const pct = (val / 25) * 100;
        let color = "var(--accent-emerald)";
        if (complexity > 10) color = "var(--accent-rose)";
        else if (complexity > 5) color = "var(--accent-amber)";

        return `
            <div class="flex items-center gap-2">
                <div style="width: 60px; height: 6px; border-radius: var(--radius-full); background: var(--bg-tertiary); overflow: hidden;">
                    <div style="width: ${pct}%; height: 100%; background: ${color};"></div>
                </div>
                <span class="font-mono text-xs">${complexity}</span>
            </div>
        `;
    }
}
