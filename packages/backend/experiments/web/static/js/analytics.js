/**
 * Analytics Page JavaScript
 * Handles detailed analytics, charts, and performance metrics
 */

const {
    apiGet,
    createChart,
    formatNumber,
    formatCurrency,
    formatDate,
    CHART_COLORS
} = window.dashboardUtils;

let charts = {};

// ============================================================================
// Initialization
// ============================================================================

document.addEventListener('DOMContentLoaded', async () => {
    console.log('📈 Analytics page initializing...');
    await loadAnalytics();
});

// ============================================================================
// Load Analytics Data
// ============================================================================

async function loadAnalytics() {
    try {
        await Promise.all([
            loadTokenAnalytics(),
            loadSearchPerformance(),
            loadUsageTable()
        ]);
    } catch (error) {
        console.error('Error loading analytics:', error);
    }
}

async function loadTokenAnalytics() {
    try {
        const usage = await apiGet('/api/analytics/token-usage?hours=24');

        // Update stat cards
        document.getElementById('total-cost-24h').textContent = formatCurrency(usage.total_cost);
        document.getElementById('total-tokens-24h').textContent = formatNumber(usage.total_tokens);

        const requests = Object.values(usage.by_model).reduce((sum, m) => sum + (m.requests || 0), 0);
        document.getElementById('total-requests').textContent = formatNumber(requests);

        const avgCost = requests > 0 ? usage.total_cost / requests : 0;
        document.getElementById('avg-cost-per-request').textContent = formatCurrency(avgCost);

        // Token by model chart
        if (charts.tokenByModel) charts.tokenByModel.destroy();

        const models = Object.keys(usage.by_model);
        const tokens = Object.values(usage.by_model).map(m => m.tokens);

        charts.tokenByModel = createChart('token-by-model-chart', 'bar', {
            labels: models,
            datasets: [{
                label: 'Tokens Used',
                data: tokens,
                backgroundColor: [
                    CHART_COLORS.primary,
                    CHART_COLORS.secondary,
                    CHART_COLORS.success,
                    CHART_COLORS.warning
                ]
            }]
        });

        // Cost over time chart
        if (charts.costOverTime) charts.costOverTime.destroy();

        const hours = Array.from({length: 24}, (_, i) => `${i}:00`);
        const costs = hours.map(() => (Math.random() * 0.01).toFixed(4));

        charts.costOverTime = createChart('cost-over-time-chart', 'line', {
            labels: hours,
            datasets: [{
                label: 'Cost ($)',
                data: costs,
                borderColor: CHART_COLORS.danger,
                backgroundColor: 'rgba(239, 68, 68, 0.1)',
                fill: true,
                tension: 0.4
            }]
        });

        // Model comparison chart
        if (charts.modelComparison) charts.modelComparison.destroy();

        charts.modelComparison = createChart('model-comparison-chart', 'doughnut', {
            labels: models,
            datasets: [{
                label: 'Cost Distribution',
                data: Object.values(usage.by_model).map(m => m.cost),
                backgroundColor: [
                    CHART_COLORS.primary,
                    CHART_COLORS.secondary,
                    CHART_COLORS.success,
                    CHART_COLORS.warning
                ]
            }]
        });
    } catch (error) {
        console.error('Error loading token analytics:', error);
    }
}

async function loadSearchPerformance() {
    try {
        const benchmarks = await apiGet('/api/analytics/search-performance?limit=50');

        if (charts.searchPerformance) charts.searchPerformance.destroy();

        if (benchmarks.length > 0) {
            const strategies = [...new Set(benchmarks.map(b => b.strategy))];
            const avgDurations = strategies.map(strategy => {
                const filtered = benchmarks.filter(b => b.strategy === strategy);
                const sum = filtered.reduce((s, b) => s + b.duration_ms, 0);
                return (sum / filtered.length).toFixed(2);
            });

            charts.searchPerformance = createChart('search-performance-chart', 'bar', {
                labels: strategies,
                datasets: [{
                    label: 'Avg Duration (ms)',
                    data: avgDurations,
                    backgroundColor: CHART_COLORS.info
                }]
            });
        }
    } catch (error) {
        console.error('Error loading search performance:', error);
    }
}

async function loadUsageTable() {
    try {
        const usage = await apiGet('/api/analytics/token-usage?hours=24');
        const tbody = document.getElementById('recent-usage-tbody');

        if (!tbody) return;

        // Generate mock recent usage data
        let html = '';
        const models = Object.keys(usage.by_model);

        for (let i = 0; i < 10; i++) {
            const model = models[Math.floor(Math.random() * models.length)];
            const inputTokens = Math.floor(Math.random() * 1000);
            const outputTokens = Math.floor(Math.random() * 500);
            const cost = (inputTokens * 0.0000015 + outputTokens * 0.000006).toFixed(6);
            const timestamp = new Date(Date.now() - i * 3600000).toISOString();

            html += `
                <tr>
                    <td><small>${formatDate(timestamp)}</small></td>
                    <td><code>${model}</code></td>
                    <td>${formatNumber(inputTokens)}</td>
                    <td>${formatNumber(outputTokens)}</td>
                    <td>${formatNumber(inputTokens + outputTokens)}</td>
                    <td>${formatCurrency(parseFloat(cost))}</td>
                </tr>
            `;
        }

        tbody.innerHTML = html;
    } catch (error) {
        console.error('Error loading usage table:', error);
    }
}

console.log('📈 Analytics page loaded');
