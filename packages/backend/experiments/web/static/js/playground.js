/**
 * Playground Page JavaScript
 * Interactive testing ground for search, memory creation, and agent features
 */

const {
    apiGet,
    apiPost,
    showNotification,
    WebSocketManager
} = window.dashboardUtils;

let ws = null;
let consoleLines = [];

// ============================================================================
// Initialization
// ============================================================================

document.addEventListener('DOMContentLoaded', () => {
    console.log('🎮 Playground initializing...');
    setupEventListeners();
});

// ============================================================================
// Search Testing
// ============================================================================

async function runSearchTest() {
    const query = document.getElementById('pg-search-query').value;
    const strategy = document.getElementById('pg-search-strategy').value;
    const limit = document.getElementById('pg-search-limit').value;
    const resultsDiv = document.getElementById('search-results-playground');

    if (!query) {
        showNotification('Please enter a search query', 'error');
        return;
    }

    logToConsole(`Running search: "${query}" with strategy: ${strategy}`);

    try {
        resultsDiv.innerHTML = '<p class="text-muted">Searching...</p>';

        // Mock search results
        const results = [
            {
                content: `Found relevant memory for: "${query}"`,
                score: 0.92,
                memory_type: 'fact',
                id: '123'
            },
            {
                content: `Another match using ${strategy} strategy`,
                score: 0.85,
                memory_type: 'preference',
                id: '456'
            }
        ];

        let html = '<div class="results-list">';
        results.forEach((result, i) => {
            html += `
                <div style="padding: 1rem; background: rgba(79, 70, 229, 0.1); border-radius: 0.5rem; margin-bottom: 0.5rem;">
                    <div style="display: flex; justify-content: space-between;">
                        <strong>${result.memory_type}</strong>
                        <span class="badge badge-primary">Score: ${(result.score * 100).toFixed(0)}%</span>
                    </div>
                    <p style="margin-top: 0.5rem; color: var(--text-secondary);">${result.content}</p>
                    <small style="color: var(--text-muted);">ID: ${result.id}</small>
                </div>
            `;
        });
        html += '</div>';

        resultsDiv.innerHTML = html;
        logToConsole(`Search completed: ${results.length} results found`, 'success');
        showNotification('Search completed successfully', 'success');
    } catch (error) {
        logToConsole(`Search failed: ${error.message}`, 'error');
        resultsDiv.innerHTML = '<p style="color: var(--danger);">Search failed</p>';
    }
}

// ============================================================================
// Memory Creation
// ============================================================================

async function createTestMemory() {
    const content = document.getElementById('pg-memory-content').value;
    const type = document.getElementById('pg-memory-type').value;
    const categoriesStr = document.getElementById('pg-memory-categories').value;
    const resultDiv = document.getElementById('create-memory-result');

    if (!content) {
        showNotification('Please enter memory content', 'error');
        return;
    }

    logToConsole(`Creating ${type} memory...`);

    try {
        const categories = categoriesStr.split(',').map(c => c.trim()).filter(c => c);

        // Mock memory creation
        const memory = {
            id: Math.random().toString(36).substr(2, 9),
            content,
            memory_type: type,
            metadata: { categories }
        };

        resultDiv.innerHTML = `
            <div style="padding: 1rem; background: rgba(16, 185, 129, 0.1); border: 1px solid var(--success); border-radius: 0.5rem; margin-top: 1rem;">
                <strong>✓ Memory Created Successfully</strong>
                <p style="margin-top: 0.5rem; color: var(--text-secondary);">
                    <strong>ID:</strong> <code>${memory.id}</code><br/>
                    <strong>Type:</strong> ${memory.memory_type}<br/>
                    <strong>Categories:</strong> ${categories.join(', ') || 'None'}
                </p>
            </div>
        `;

        logToConsole(`Memory created: ${memory.id}`, 'success');
        showNotification('Memory created successfully', 'success');

        // Clear form
        document.getElementById('pg-memory-content').value = '';
        document.getElementById('pg-memory-categories').value = '';
    } catch (error) {
        logToConsole(`Failed to create memory: ${error.message}`, 'error');
        resultDiv.innerHTML = '<p style="color: var(--danger);">Failed to create memory</p>';
    }
}

// ============================================================================
// Fact Extraction
// ============================================================================

async function extractFacts() {
    const text = document.getElementById('pg-extract-text').value;
    const resultDiv = document.getElementById('extracted-facts-result');

    if (!text) {
        showNotification('Please enter text to extract from', 'error');
        return;
    }

    logToConsole('Extracting facts...');

    try {
        resultDiv.innerHTML = '<p class="text-muted">Extracting facts...</p>';

        // Mock fact extraction
        const facts = [
            {
                fact: "User loves programming in Python",
                category: "programming",
                confidence: 0.95
            },
            {
                fact: "User prefers dark mode in IDE",
                category: "preferences",
                confidence: 0.90
            },
            {
                fact: "User works best in the mornings",
                category: "work-habits",
                confidence: 0.85
            }
        ];

        let html = '<div style="margin-top: 1rem;">';
        html += `<p><strong>${facts.length} facts extracted:</strong></p>`;
        facts.forEach((fact, i) => {
            html += `
                <div style="padding: 0.75rem; background: rgba(0, 0, 0, 0.2); border-left: 3px solid var(--success); border-radius: 0.375rem; margin-top: 0.5rem;">
                    <p style="margin-bottom: 0.25rem;">${fact.fact}</p>
                    <div style="display: flex; gap: 0.5rem; margin-top: 0.5rem;">
                        <span class="badge badge-info">${fact.category}</span>
                        <span class="badge badge-success">Confidence: ${(fact.confidence * 100).toFixed(0)}%</span>
                    </div>
                </div>
            `;
        });
        html += '</div>';

        resultDiv.innerHTML = html;
        logToConsole(`Extracted ${facts.length} facts`, 'success');
        showNotification('Fact extraction completed', 'success');
    } catch (error) {
        logToConsole(`Fact extraction failed: ${error.message}`, 'error');
        resultDiv.innerHTML = '<p style="color: var(--danger);">Extraction failed</p>';
    }
}

// ============================================================================
// Performance Benchmark
// ============================================================================

async function runBenchmark() {
    const queriesText = document.getElementById('pg-bench-queries').value;
    const resultDiv = document.getElementById('benchmark-results');

    if (!queriesText) {
        showNotification('Please enter queries to benchmark', 'error');
        return;
    }

    const queries = queriesText.split('\n').filter(q => q.trim());

    if (queries.length === 0) {
        showNotification('No valid queries found', 'error');
        return;
    }

    logToConsole(`Running benchmark with ${queries.length} queries...`);

    try {
        resultDiv.innerHTML = '<p class="text-muted">Running benchmark...</p>';

        const results = queries.map(query => ({
            query,
            duration: Math.random() * 100 + 20,
            results: Math.floor(Math.random() * 10) + 1
        }));

        const avgDuration = results.reduce((sum, r) => sum + r.duration, 0) / results.length;

        let html = '<div style="margin-top: 1rem;">';
        html += `<p><strong>Benchmark Results:</strong></p>`;
        html += `<p>Average duration: <strong>${avgDuration.toFixed(2)}ms</strong></p>`;
        html += '<table class="data-table" style="margin-top: 1rem;">';
        html += '<thead><tr><th>Query</th><th>Duration (ms)</th><th>Results</th></tr></thead>';
        html += '<tbody>';
        results.forEach(r => {
            html += `
                <tr>
                    <td>${r.query}</td>
                    <td>${r.duration.toFixed(2)}</td>
                    <td>${r.results}</td>
                </tr>
            `;
        });
        html += '</tbody></table></div>';

        resultDiv.innerHTML = html;
        logToConsole(`Benchmark completed: avg ${avgDuration.toFixed(2)}ms`, 'success');
        showNotification('Benchmark completed', 'success');
    } catch (error) {
        logToConsole(`Benchmark failed: ${error.message}`, 'error');
        resultDiv.innerHTML = '<p style="color: var(--danger);">Benchmark failed</p>';
    }
}

// ============================================================================
// WebSocket
// ============================================================================

function toggleWebSocket() {
    const button = document.getElementById('ws-toggle-text');
    const statusDot = document.getElementById('ws-status-dot');
    const statusText = document.getElementById('ws-status-text');

    if (!ws || ws.ws?.readyState !== WebSocket.OPEN) {
        // Connect
        const wsUrl = `ws://${window.location.host}/ws/updates`;
        ws = new WebSocketManager(wsUrl);

        ws.on('open', () => {
            button.textContent = 'Disconnect';
            statusDot.className = 'status-dot status-connected';
            statusText.textContent = 'Connected';
            logToConsole('WebSocket connected', 'success');
        });

        ws.on('message', (data) => {
            logToConsole(`WebSocket message: ${JSON.stringify(data)}`);
        });

        ws.on('close', () => {
            button.textContent = 'Connect';
            statusDot.className = 'status-dot status-disconnected';
            statusText.textContent = 'Disconnected';
            logToConsole('WebSocket disconnected');
        });

        ws.on('error', (error) => {
            logToConsole(`WebSocket error: ${error}`, 'error');
        });

        ws.connect();
    } else {
        // Disconnect
        ws.disconnect();
    }
}

// ============================================================================
// Console
// ============================================================================

function logToConsole(message, type = 'info') {
    const consoleDiv = document.getElementById('live-console');
    if (!consoleDiv) return;

    const timestamp = new Date().toLocaleTimeString();
    const colorClass = type === 'error' ? 'console-error' : type === 'success' ? 'console-success' : 'console-message';

    const line = document.createElement('div');
    line.className = 'console-line';
    line.innerHTML = `
        <span class="console-timestamp">[${timestamp}]</span>
        <span class="${colorClass}">${message}</span>
    `;

    consoleDiv.appendChild(line);
    consoleDiv.scrollTop = consoleDiv.scrollHeight;

    consoleLines.push({ timestamp, message, type });
}

function clearConsole() {
    const consoleDiv = document.getElementById('live-console');
    if (consoleDiv) {
        consoleDiv.innerHTML = '';
        consoleLines = [];
        logToConsole('Console cleared');
    }
}

// ============================================================================
// Event Listeners
// ============================================================================

function setupEventListeners() {
    // Add CSS for console colors
    const style = document.createElement('style');
    style.textContent = `
        .console-error { color: #ef4444; }
        .console-success { color: #10b981; }
        .console-message { color: #10b981; }
    `;
    document.head.appendChild(style);
}

// Make functions globally available
window.runSearchTest = runSearchTest;
window.createTestMemory = createTestMemory;
window.extractFacts = extractFacts;
window.runBenchmark = runBenchmark;
window.toggleWebSocket = toggleWebSocket;
window.clearConsole = clearConsole;

console.log('🎮 Playground loaded');
