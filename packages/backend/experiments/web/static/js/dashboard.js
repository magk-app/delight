/**
 * Dashboard Page JavaScript
 * Handles dashboard statistics, charts, and real-time updates
 */

const {
    apiGet,
    apiPost,
    showNotification,
    createChart,
    formatNumber,
    formatCurrency,
    formatRelativeTime,
    updateElement,
    CHART_COLORS
} = window.dashboardUtils;

// Charts
let memoryTypeChart = null;
let categoryChart = null;
let tokenUsageChart = null;

// ============================================================================
// Initialization
// ============================================================================

document.addEventListener('DOMContentLoaded', async () => {
    console.log('🚀 Dashboard initializing...');
    await loadDashboardData();
    setupEventListeners();
    startAutoRefresh();
});

// ============================================================================
// Data Loading
// ============================================================================

async function loadDashboardData() {
    try {
        await Promise.all([
            loadMemoryStats(),
            loadTokenUsage(),
            loadSystemInfo(),
            loadRecentActivity()
        ]);
        showNotification('Dashboard loaded successfully', 'success');
    } catch (error) {
        console.error('Error loading dashboard:', error);
        showNotification('Failed to load dashboard data', 'error');
    }
}

async function loadMemoryStats() {
    try {
        const stats = await apiGet('/api/analytics/stats');

        // Update stat cards
        updateElement('total-memories', formatNumber(stats.total_memories));
        updateElement('total-embeddings', formatNumber(stats.total_embeddings));

        // Memory type chart
        if (memoryTypeChart) memoryTypeChart.destroy();

        const typeLabels = Object.keys(stats.by_type);
        const typeData = Object.values(stats.by_type);

        memoryTypeChart = createChart('memory-type-chart', 'doughnut', {
            labels: typeLabels,
            datasets: [{
                data: typeData,
                backgroundColor: [
                    CHART_COLORS.primary,
                    CHART_COLORS.secondary,
                    CHART_COLORS.success,
                    CHART_COLORS.warning,
                    CHART_COLORS.purple,
                    CHART_COLORS.pink
                ]
            }]
        });

        // Category chart
        if (categoryChart) categoryChart.destroy();

        const categoryLabels = Object.keys(stats.by_category).slice(0, 10);
        const categoryData = Object.values(stats.by_category).slice(0, 10);

        categoryChart = createChart('category-chart', 'bar', {
            labels: categoryLabels,
            datasets: [{
                label: 'Memories',
                data: categoryData,
                backgroundColor: CHART_COLORS.secondary
            }]
        });
    } catch (error) {
        console.error('Error loading memory stats:', error);
    }
}

async function loadTokenUsage() {
    try {
        const usage = await apiGet('/api/analytics/token-usage?hours=24');

        // Update stat cards
        updateElement('total-cost', formatCurrency(usage.total_cost));
        updateElement('total-tokens', formatNumber(usage.total_tokens));

        // Update model usage table
        const tbody = document.getElementById('model-usage-tbody');
        if (tbody && usage.by_model) {
            let html = '';
            for (const [model, data] of Object.entries(usage.by_model)) {
                html += `
                    <tr>
                        <td><strong>${model}</strong></td>
                        <td>${formatNumber(data.tokens)}</td>
                        <td>${formatCurrency(data.cost)}</td>
                        <td>${data.requests || '-'}</td>
                    </tr>
                `;
            }
            tbody.innerHTML = html || '<tr><td colspan="4" class="text-center">No data available</td></tr>';
        }

        // Token usage over time chart
        if (tokenUsageChart) tokenUsageChart.destroy();

        // Generate mock time series data (in production, this would come from API)
        const hours = Array.from({length: 24}, (_, i) => `${i}:00`);
        const tokenData = hours.map(() => Math.floor(Math.random() * 1000));

        tokenUsageChart = createChart('token-usage-chart', 'line', {
            labels: hours,
            datasets: [{
                label: 'Tokens Used',
                data: tokenData,
                borderColor: CHART_COLORS.primary,
                backgroundColor: 'rgba(79, 70, 229, 0.1)',
                fill: true,
                tension: 0.4
            }]
        }, {
            plugins: {
                legend: {
                    display: false
                }
            }
        });
    } catch (error) {
        console.error('Error loading token usage:', error);
    }
}

async function loadSystemInfo() {
    try {
        const config = await apiGet('/api/config');

        updateElement('chat-model', config.models.chat_model);
        updateElement('embedding-model', config.models.embedding_model);
    } catch (error) {
        console.error('Error loading system info:', error);
    }
}

async function loadRecentActivity() {
    try {
        const memories = await apiGet('/api/memories?limit=5');
        const activityDiv = document.getElementById('recent-activity');

        if (activityDiv) {
            if (memories.length === 0) {
                activityDiv.innerHTML = '<p class="text-muted">No recent activity</p>';
            } else {
                let html = '';
                memories.forEach(memory => {
                    html += `
                        <div class="activity-item">
                            <strong>${memory.memory_type}</strong>
                            <p style="color: var(--text-muted); font-size: 0.875rem; margin-top: 0.25rem;">
                                ${memory.content.substring(0, 100)}${memory.content.length > 100 ? '...' : ''}
                            </p>
                            <small style="color: var(--text-muted);">${formatRelativeTime(memory.created_at)}</small>
                        </div>
                    `;
                });
                activityDiv.innerHTML = html;
            }
        }
    } catch (error) {
        console.error('Error loading recent activity:', error);
    }
}

// ============================================================================
// Search Modal
// ============================================================================

function testSearch() {
    const modal = document.getElementById('search-modal');
    if (modal) {
        modal.classList.add('active');
    }
}

function closeSearchModal() {
    const modal = document.getElementById('search-modal');
    if (modal) {
        modal.classList.remove('active');
    }
}

async function executeSearch() {
    const query = document.getElementById('search-query').value;
    const strategy = document.getElementById('search-strategy').value;
    const resultsDiv = document.getElementById('search-results');

    if (!query) {
        showNotification('Please enter a search query', 'error');
        return;
    }

    if (resultsDiv) {
        resultsDiv.innerHTML = '<p class="text-muted">Searching...</p>';
    }

    try {
        // In production, this would call the actual search API
        // For now, show a demo result
        const demoResults = [
            {
                content: `Demo result for "${query}" using ${strategy} strategy`,
                score: 0.95,
                memory_type: 'fact'
            }
        ];

        let html = '<div style="margin-top: 1rem;">';
        html += '<h3>Search Results:</h3>';
        demoResults.forEach((result, i) => {
            html += `
                <div style="padding: 1rem; background: rgba(79, 70, 229, 0.1); border-radius: 0.5rem; margin-top: 0.5rem;">
                    <div style="display: flex; justify-content: space-between; align-items: start;">
                        <strong>${result.memory_type}</strong>
                        <span class="badge badge-primary">Score: ${(result.score * 100).toFixed(0)}%</span>
                    </div>
                    <p style="margin-top: 0.5rem;">${result.content}</p>
                </div>
            `;
        });
        html += '</div>';

        if (resultsDiv) {
            resultsDiv.innerHTML = html;
        }

        showNotification('Search completed', 'success');
    } catch (error) {
        console.error('Search error:', error);
        if (resultsDiv) {
            resultsDiv.innerHTML = '<p style="color: var(--danger);">Search failed. Please try again.</p>';
        }
    }
}

// ============================================================================
// Quick Actions
// ============================================================================

function exportData() {
    showNotification('Export functionality coming soon!', 'info');
}

async function refreshAllData() {
    showNotification('Refreshing dashboard...', 'info');
    await loadDashboardData();
}

// ============================================================================
// Event Listeners
// ============================================================================

function setupEventListeners() {
    // Close modal when clicking outside
    const modal = document.getElementById('search-modal');
    if (modal) {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                closeSearchModal();
            }
        });
    }

    // Time range selector
    const timeRange = document.getElementById('time-range');
    if (timeRange) {
        timeRange.addEventListener('change', async () => {
            await loadTokenUsage();
        });
    }

    // Enter key in search modal
    const searchQuery = document.getElementById('search-query');
    if (searchQuery) {
        searchQuery.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                executeSearch();
            }
        });
    }
}

// ============================================================================
// Auto Refresh
// ============================================================================

function startAutoRefresh() {
    // Refresh dashboard every 30 seconds
    setInterval(async () => {
        await loadMemoryStats();
        await loadTokenUsage();
    }, 30000);
}

// Make functions globally available
window.testSearch = testSearch;
window.closeSearchModal = closeSearchModal;
window.executeSearch = executeSearch;
window.exportData = exportData;
window.refreshAllData = refreshAllData;

console.log('📊 Dashboard loaded');
