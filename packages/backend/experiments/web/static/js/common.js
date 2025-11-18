/**
 * Common JavaScript utilities for Experimental Agent Dashboard
 * Shared functions, API helpers, and global utilities
 */

// API Base URL
const API_BASE = window.location.origin;

// ============================================================================
// API Helper Functions
// ============================================================================

/**
 * Generic API request helper with error handling
 */
async function apiRequest(endpoint, options = {}) {
    try {
        const response = await fetch(`${API_BASE}${endpoint}`, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        return await response.json();
    } catch (error) {
        console.error(`API Error (${endpoint}):`, error);
        showNotification(`API Error: ${error.message}`, 'error');
        throw error;
    }
}

/**
 * GET request helper
 */
async function apiGet(endpoint) {
    return apiRequest(endpoint, { method: 'GET' });
}

/**
 * POST request helper
 */
async function apiPost(endpoint, data) {
    return apiRequest(endpoint, {
        method: 'POST',
        body: JSON.stringify(data)
    });
}

/**
 * DELETE request helper
 */
async function apiDelete(endpoint) {
    return apiRequest(endpoint, { method: 'DELETE' });
}

// ============================================================================
// Notification System
// ============================================================================

function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 1rem 1.5rem;
        background: ${type === 'error' ? '#ef4444' : type === 'success' ? '#10b981' : '#3b82f6'};
        color: white;
        border-radius: 0.5rem;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.4);
        z-index: 10000;
        animation: slideIn 0.3s ease-out;
    `;

    document.body.appendChild(notification);

    // Auto-remove after 5 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease-in';
        setTimeout(() => notification.remove(), 300);
    }, 5000);
}

// Add CSS animations for notifications
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

// ============================================================================
// Chart Helpers
// ============================================================================

const CHART_COLORS = {
    primary: '#4f46e5',
    secondary: '#06b6d4',
    success: '#10b981',
    warning: '#f59e0b',
    danger: '#ef4444',
    info: '#3b82f6',
    purple: '#8b5cf6',
    pink: '#ec4899'
};

const CHART_DEFAULTS = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
        legend: {
            labels: {
                color: '#cbd5e1',
                font: {
                    family: "'Inter', sans-serif",
                    size: 12
                }
            }
        },
        tooltip: {
            backgroundColor: 'rgba(15, 23, 42, 0.9)',
            titleColor: '#f1f5f9',
            bodyColor: '#cbd5e1',
            borderColor: '#334155',
            borderWidth: 1,
            padding: 12,
            cornerRadius: 8
        }
    },
    scales: {
        x: {
            ticks: {
                color: '#94a3b8'
            },
            grid: {
                color: 'rgba(148, 163, 184, 0.1)'
            }
        },
        y: {
            ticks: {
                color: '#94a3b8'
            },
            grid: {
                color: 'rgba(148, 163, 184, 0.1)'
            }
        }
    }
};

function createChart(canvasId, type, data, options = {}) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) {
        console.error(`Canvas element '${canvasId}' not found`);
        return null;
    }

    return new Chart(ctx, {
        type,
        data,
        options: {
            ...CHART_DEFAULTS,
            ...options
        }
    });
}

// ============================================================================
// Data Formatting
// ============================================================================

function formatNumber(num) {
    if (num >= 1000000) {
        return (num / 1000000).toFixed(1) + 'M';
    }
    if (num >= 1000) {
        return (num / 1000).toFixed(1) + 'K';
    }
    return num.toFixed(0);
}

function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 2,
        maximumFractionDigits: 4
    }).format(amount);
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    }).format(date);
}

function formatRelativeTime(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diff = now - date;
    const seconds = Math.floor(diff / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);

    if (seconds < 60) return 'just now';
    if (minutes < 60) return `${minutes}m ago`;
    if (hours < 24) return `${hours}h ago`;
    if (days < 30) return `${days}d ago`;
    return formatDate(dateString);
}

// ============================================================================
// DOM Helpers
// ============================================================================

function updateElement(id, value) {
    const el = document.getElementById(id);
    if (el) {
        el.textContent = value;
    }
}

function showElement(id) {
    const el = document.getElementById(id);
    if (el) {
        el.style.display = 'block';
    }
}

function hideElement(id) {
    const el = document.getElementById(id);
    if (el) {
        el.style.display = 'none';
    }
}

function toggleElement(id) {
    const el = document.getElementById(id);
    if (el) {
        el.style.display = el.style.display === 'none' ? 'block' : 'none';
    }
}

// ============================================================================
// Loading States
// ============================================================================

function showLoading(elementId) {
    const el = document.getElementById(elementId);
    if (el) {
        el.innerHTML = '<div class="loading-spinner">Loading...</div>';
    }
}

function hideLoading(elementId) {
    const el = document.getElementById(elementId);
    if (el) {
        el.innerHTML = '';
    }
}

// ============================================================================
// WebSocket Helper
// ============================================================================

class WebSocketManager {
    constructor(url) {
        this.url = url;
        this.ws = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.handlers = {
            open: [],
            message: [],
            close: [],
            error: []
        };
    }

    connect() {
        try {
            this.ws = new WebSocket(this.url);

            this.ws.onopen = (event) => {
                console.log('WebSocket connected');
                this.reconnectAttempts = 0;
                this.handlers.open.forEach(handler => handler(event));
            };

            this.ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                this.handlers.message.forEach(handler => handler(data));
            };

            this.ws.onclose = (event) => {
                console.log('WebSocket disconnected');
                this.handlers.close.forEach(handler => handler(event));
                this.attemptReconnect();
            };

            this.ws.onerror = (error) => {
                console.error('WebSocket error:', error);
                this.handlers.error.forEach(handler => handler(error));
            };
        } catch (error) {
            console.error('Failed to create WebSocket:', error);
        }
    }

    disconnect() {
        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }
    }

    send(data) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify(data));
        }
    }

    on(event, handler) {
        if (this.handlers[event]) {
            this.handlers[event].push(handler);
        }
    }

    attemptReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);
            setTimeout(() => this.connect(), 2000 * this.reconnectAttempts);
        }
    }
}

// ============================================================================
// Export for use in other files
// ============================================================================

window.dashboardUtils = {
    apiGet,
    apiPost,
    apiDelete,
    showNotification,
    createChart,
    formatNumber,
    formatCurrency,
    formatDate,
    formatRelativeTime,
    updateElement,
    showElement,
    hideElement,
    toggleElement,
    showLoading,
    hideLoading,
    WebSocketManager,
    CHART_COLORS,
    CHART_DEFAULTS
};

console.log('🎯 Dashboard utilities loaded');
