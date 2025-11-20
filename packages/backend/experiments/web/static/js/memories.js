/**
 * Memories Page JavaScript
 * Handles memory browsing, graph visualization, and memory management
 */

const {
    apiGet,
    apiDelete,
    showNotification,
    formatRelativeTime
} = window.dashboardUtils;

let allMemories = [];
let filteredMemories = [];
let currentView = 'list';
let graphSimulation = null;
let currentMemoryId = null;

// ============================================================================
// Initialization
// ============================================================================

document.addEventListener('DOMContentLoaded', async () => {
    console.log('🧠 Memories page initializing...');
    await refreshMemories();
    setupEventListeners();
});

// ============================================================================
// Data Loading
// ============================================================================

async function refreshMemories() {
    try {
        allMemories = await apiGet('/api/memories?limit=100');
        filteredMemories = [...allMemories];

        updateMemoryCount();
        renderMemoriesList();
        populateCategoryFilter();

        if (currentView === 'graph') {
            renderKnowledgeGraph();
        }

        showNotification('Memories refreshed', 'success');
    } catch (error) {
        console.error('Error loading memories:', error);
        showNotification('Failed to load memories', 'error');
    }
}

// ============================================================================
// Filtering
// ============================================================================

function applyFilters() {
    const typeFilter = document.getElementById('memory-type-filter').value;
    const categoryFilter = document.getElementById('category-filter').value;
    const searchQuery = document.getElementById('memory-search').value.toLowerCase();

    filteredMemories = allMemories.filter(memory => {
        // Type filter
        if (typeFilter && memory.memory_type !== typeFilter) {
            return false;
        }

        // Category filter
        if (categoryFilter) {
            const categories = memory.metadata?.categories || [];
            if (!categories.includes(categoryFilter)) {
                return false;
            }
        }

        // Search filter
        if (searchQuery && !memory.content.toLowerCase().includes(searchQuery)) {
            return false;
        }

        return true;
    });

    updateMemoryCount();
    renderMemoriesList();

    if (currentView === 'graph') {
        renderKnowledgeGraph();
    }
}

function populateCategoryFilter() {
    const categorySet = new Set();
    allMemories.forEach(memory => {
        const categories = memory.metadata?.categories || [];
        categories.forEach(cat => categorySet.add(cat));
    });

    const select = document.getElementById('category-filter');
    if (select) {
        const currentValue = select.value;
        let html = '<option value="">All Categories</option>';
        Array.from(categorySet).sort().forEach(category => {
            html += `<option value="${category}">${category}</option>`;
        });
        select.innerHTML = html;
        select.value = currentValue;
    }
}

function updateMemoryCount() {
    const countEl = document.getElementById('memory-count');
    if (countEl) {
        countEl.textContent = `${filteredMemories.length} memories`;
    }
}

// ============================================================================
// List View
// ============================================================================

function renderMemoriesList() {
    const listDiv = document.getElementById('memories-list');
    if (!listDiv) return;

    if (filteredMemories.length === 0) {
        listDiv.innerHTML = '<p class="text-muted">No memories found</p>';
        return;
    }

    let html = '';
    filteredMemories.forEach(memory => {
        const categories = memory.metadata?.categories || [];
        const categoryBadges = categories.map(cat =>
            `<span class="badge badge-info" style="margin-right: 0.25rem;">${cat}</span>`
        ).join('');

        html += `
            <div class="memory-item" onclick="showMemoryDetail('${memory.id}')">
                <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 0.5rem;">
                    <strong>${memory.memory_type}</strong>
                    <small style="color: var(--text-muted);">${formatRelativeTime(memory.created_at)}</small>
                </div>
                <p style="color: var(--text-secondary); margin-bottom: 0.5rem;">
                    ${memory.content.substring(0, 200)}${memory.content.length > 200 ? '...' : ''}
                </p>
                ${categoryBadges ? `<div>${categoryBadges}</div>` : ''}
            </div>
        `;
    });

    listDiv.innerHTML = html;
}

// ============================================================================
// Graph View
// ============================================================================

function renderKnowledgeGraph() {
    const svg = d3.select('#knowledge-graph');
    const width = svg.node().getBoundingClientRect().width;
    const height = 600;

    svg.selectAll('*').remove();

    if (filteredMemories.length === 0) {
        svg.append('text')
            .attr('x', width / 2)
            .attr('y', height / 2)
            .attr('text-anchor', 'middle')
            .attr('fill', '#94a3b8')
            .text('No memories to visualize');
        return;
    }

    // Prepare nodes and links
    const nodes = filteredMemories.map(m => ({
        id: m.id,
        type: m.memory_type,
        label: m.content.substring(0, 30) + '...',
        fullContent: m.content
    }));

    const links = [];
    // In a real implementation, extract relationships from metadata

    // Color scale
    const colorScale = d3.scaleOrdinal()
        .domain(['fact', 'preference', 'context', 'episodic'])
        .range(['#4f46e5', '#06b6d4', '#10b981', '#f59e0b']);

    // Create force simulation
    graphSimulation = d3.forceSimulation(nodes)
        .force('link', d3.forceLink(links).id(d => d.id).distance(100))
        .force('charge', d3.forceManyBody().strength(-300))
        .force('center', d3.forceCenter(width / 2, height / 2))
        .force('collision', d3.forceCollide().radius(30));

    // Create links
    const link = svg.append('g')
        .selectAll('line')
        .data(links)
        .join('line')
        .attr('stroke', '#334155')
        .attr('stroke-width', 2);

    // Create nodes
    const node = svg.append('g')
        .selectAll('circle')
        .data(nodes)
        .join('circle')
        .attr('r', 20)
        .attr('fill', d => colorScale(d.type))
        .attr('stroke', '#1e293b')
        .attr('stroke-width', 2)
        .style('cursor', 'pointer')
        .on('click', (event, d) => {
            showMemoryDetail(d.id);
        })
        .call(d3.drag()
            .on('start', dragstarted)
            .on('drag', dragged)
            .on('end', dragended));

    // Add labels
    const label = svg.append('g')
        .selectAll('text')
        .data(nodes)
        .join('text')
        .text(d => d.label)
        .attr('font-size', 10)
        .attr('fill', '#cbd5e1')
        .attr('text-anchor', 'middle')
        .attr('dy', 35);

    // Update positions on tick
    graphSimulation.on('tick', () => {
        link
            .attr('x1', d => d.source.x)
            .attr('y1', d => d.source.y)
            .attr('x2', d => d.target.x)
            .attr('y2', d => d.target.y);

        node
            .attr('cx', d => d.x)
            .attr('cy', d => d.y);

        label
            .attr('x', d => d.x)
            .attr('y', d => d.y);
    });

    function dragstarted(event, d) {
        if (!event.active) graphSimulation.alphaTarget(0.3).restart();
        d.fx = d.x;
        d.fy = d.y;
    }

    function dragged(event, d) {
        d.fx = event.x;
        d.fy = event.y;
    }

    function dragended(event, d) {
        if (!event.active) graphSimulation.alphaTarget(0);
        d.fx = null;
        d.fy = null;
    }
}

// ============================================================================
// View Toggle
// ============================================================================

function toggleView() {
    currentView = currentView === 'list' ? 'graph' : 'list';

    const listView = document.getElementById('list-view');
    const graphView = document.getElementById('graph-view');
    const toggleIcon = document.getElementById('view-toggle-icon');
    const toggleText = document.getElementById('view-toggle-text');

    if (currentView === 'list') {
        listView.classList.add('active');
        graphView.classList.remove('active');
        toggleIcon.textContent = '📊';
        toggleText.textContent = 'Graph View';
    } else {
        listView.classList.remove('active');
        graphView.classList.add('active');
        toggleIcon.textContent = '📋';
        toggleText.textContent = 'List View';
        renderKnowledgeGraph();
    }
}

// ============================================================================
// Memory Detail Modal
// ============================================================================

function showMemoryDetail(memoryId) {
    const memory = allMemories.find(m => m.id === memoryId);
    if (!memory) return;

    currentMemoryId = memoryId;

    const modal = document.getElementById('memory-detail-modal');
    const content = document.getElementById('memory-detail-content');

    const categories = memory.metadata?.categories || [];
    const categoryBadges = categories.map(cat =>
        `<span class="badge badge-info">${cat}</span>`
    ).join(' ');

    content.innerHTML = `
        <div style="margin-bottom: 1.5rem;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 1rem;">
                <h3>${memory.memory_type}</h3>
                <small style="color: var(--text-muted);">${formatRelativeTime(memory.created_at)}</small>
            </div>
            <p style="color: var(--text-secondary); line-height: 1.6;">
                ${memory.content}
            </p>
        </div>

        ${categories.length > 0 ? `
            <div style="margin-bottom: 1.5rem;">
                <strong>Categories:</strong><br/>
                ${categoryBadges}
            </div>
        ` : ''}

        <div style="margin-bottom: 1.5rem;">
            <strong>Memory ID:</strong><br/>
            <code style="font-family: var(--font-mono); font-size: 0.875rem; color: var(--text-muted);">
                ${memory.id}
            </code>
        </div>

        <div>
            <strong>Created:</strong> ${formatRelativeTime(memory.created_at)}<br/>
            <strong>User ID:</strong> <code>${memory.user_id}</code>
        </div>
    `;

    modal.classList.add('active');
}

function closeMemoryDetail() {
    const modal = document.getElementById('memory-detail-modal');
    modal.classList.remove('active');
    currentMemoryId = null;
}

async function deleteCurrentMemory() {
    if (!currentMemoryId) return;

    if (!confirm('Are you sure you want to delete this memory?')) {
        return;
    }

    try {
        await apiDelete(`/api/memories/${currentMemoryId}`);
        showNotification('Memory deleted successfully', 'success');
        closeMemoryDetail();
        await refreshMemories();
    } catch (error) {
        console.error('Error deleting memory:', error);
        showNotification('Failed to delete memory', 'error');
    }
}

// ============================================================================
// Graph Controls
// ============================================================================

function resetGraphZoom() {
    if (graphSimulation) {
        graphSimulation.alpha(1).restart();
    }
}

function togglePhysics() {
    const button = document.getElementById('physics-state');
    if (graphSimulation) {
        if (graphSimulation.alpha() > 0) {
            graphSimulation.stop();
            button.textContent = 'Resume';
        } else {
            graphSimulation.restart();
            button.textContent = 'Pause';
        }
    }
}

function toggleLabels() {
    const showLabels = document.getElementById('show-labels').checked;
    d3.select('#knowledge-graph')
        .selectAll('text')
        .style('display', showLabels ? 'block' : 'none');
}

// ============================================================================
// Event Listeners
// ============================================================================

function setupEventListeners() {
    // Close modal on outside click
    const modal = document.getElementById('memory-detail-modal');
    if (modal) {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                closeMemoryDetail();
            }
        });
    }
}

// Make functions globally available
window.refreshMemories = refreshMemories;
window.applyFilters = applyFilters;
window.toggleView = toggleView;
window.showMemoryDetail = showMemoryDetail;
window.closeMemoryDetail = closeMemoryDetail;
window.deleteCurrentMemory = deleteCurrentMemory;
window.resetGraphZoom = resetGraphZoom;
window.togglePhysics = togglePhysics;
window.toggleLabels = toggleLabels;

console.log('🧠 Memories page loaded');
