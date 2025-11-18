/**
 * Configuration Page JavaScript
 * Handles model configuration, search parameters, and system settings
 */

const {
    apiGet,
    apiPost,
    showNotification,
    updateElement
} = window.dashboardUtils;

let currentConfig = null;

// ============================================================================
// Initialization
// ============================================================================

document.addEventListener('DOMContentLoaded', async () => {
    console.log('⚙️ Config page initializing...');
    await loadConfig();
    setupEventListeners();
});

// ============================================================================
// Load Configuration
// ============================================================================

async function loadConfig() {
    try {
        const config = await apiGet('/api/config');
        currentConfig = config;

        // Load model settings
        document.getElementById('chat-model-select').value = config.models.chat_model;
        document.getElementById('reasoning-model-select').value = config.models.reasoning_model;
        document.getElementById('expensive-model-select').value = config.models.expensive_model;
        document.getElementById('embedding-model-select').value = config.models.embedding_model;

        // Load search settings
        document.getElementById('similarity-threshold').value = config.search.similarity_threshold;
        document.getElementById('similarity-value').textContent = config.search.similarity_threshold;
        document.getElementById('default-search-limit').value = config.search.default_search_limit;
        document.getElementById('vector-weight').value = config.search.hybrid_search_weight_vector;
        document.getElementById('vector-weight-value').textContent = config.search.hybrid_search_weight_vector;
        updateHybridWeights(config.search.hybrid_search_weight_vector);

        // Load fact extraction settings
        document.getElementById('max-facts').value = config.fact_extraction.max_facts_per_message;
        document.getElementById('min-fact-length').value = config.fact_extraction.min_fact_length;
        document.getElementById('auto-categorize').checked = config.fact_extraction.auto_categorize;
        document.getElementById('max-categories').value = config.fact_extraction.max_categories_per_fact;

        showNotification('Configuration loaded', 'success');
    } catch (error) {
        console.error('Error loading config:', error);
        showNotification('Failed to load configuration', 'error');
    }
}

// ============================================================================
// Save Configuration
// ============================================================================

async function saveConfig() {
    try {
        const config = {
            models: {
                chat_model: document.getElementById('chat-model-select').value,
                reasoning_model: document.getElementById('reasoning-model-select').value,
                expensive_model: document.getElementById('expensive-model-select').value,
                embedding_model: document.getElementById('embedding-model-select').value
            },
            search: {
                similarity_threshold: parseFloat(document.getElementById('similarity-threshold').value),
                default_search_limit: parseInt(document.getElementById('default-search-limit').value),
                hybrid_search_weight_vector: parseFloat(document.getElementById('vector-weight').value),
                graph_traversal_max_depth: 3
            },
            fact_extraction: {
                max_facts_per_message: parseInt(document.getElementById('max-facts').value),
                auto_categorize: document.getElementById('auto-categorize').checked,
                max_categories_per_fact: parseInt(document.getElementById('max-categories').value),
                min_fact_length: parseInt(document.getElementById('min-fact-length').value)
            }
        };

        await apiPost('/api/config', config);

        const statusDiv = document.getElementById('config-status');
        if (statusDiv) {
            statusDiv.className = 'alert alert-success';
            statusDiv.textContent = '✓ Configuration saved successfully';
            statusDiv.style.display = 'block';
            setTimeout(() => {
                statusDiv.style.display = 'none';
            }, 3000);
        }

        showNotification('Configuration saved successfully', 'success');
        currentConfig = config;
    } catch (error) {
        console.error('Error saving config:', error);

        const statusDiv = document.getElementById('config-status');
        if (statusDiv) {
            statusDiv.className = 'alert alert-error';
            statusDiv.textContent = '✗ Failed to save configuration';
            statusDiv.style.display = 'block';
        }

        showNotification('Failed to save configuration', 'error');
    }
}

// ============================================================================
// Tab Switching
// ============================================================================

function switchTab(tabName) {
    // Hide all tab contents
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });

    // Remove active class from all buttons
    document.querySelectorAll('.tab-button').forEach(button => {
        button.classList.remove('active');
    });

    // Show selected tab
    const selectedTab = document.getElementById(`${tabName}-tab`);
    if (selectedTab) {
        selectedTab.classList.add('active');
    }

    // Activate button
    event.target.classList.add('active');
}

// ============================================================================
// Hybrid Weight Update
// ============================================================================

function updateHybridWeights(vectorWeight) {
    const keywordWeight = (1 - parseFloat(vectorWeight)).toFixed(1);
    document.getElementById('vector-weight-value').textContent = vectorWeight;
    document.getElementById('keyword-weight').value = keywordWeight;
    document.getElementById('keyword-weight-value').textContent = keywordWeight;
}

// ============================================================================
// Event Listeners
// ============================================================================

function setupEventListeners() {
    // Model selection change handlers (update info panels)
    document.getElementById('chat-model-select').addEventListener('change', updateModelInfo);
    document.getElementById('reasoning-model-select').addEventListener('change', updateModelInfo);
    document.getElementById('expensive-model-select').addEventListener('change', updateModelInfo);
}

function updateModelInfo() {
    // Update model cost/speed info based on selection
    // This is a simplified version - in production, fetch from API
    console.log('Model selection changed');
}

// Make functions globally available
window.loadConfig = loadConfig;
window.saveConfig = saveConfig;
window.switchTab = switchTab;
window.updateHybridWeights = updateHybridWeights;

console.log('⚙️ Config page loaded');
