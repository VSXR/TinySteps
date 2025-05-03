import { escapeHtml } from './utils.js';

/**
 * Loading indicator functions
 */
function showLoading(message = 'Loading...') {
    let loadingElement = document.getElementById('loading-indicator');
    
    if (!loadingElement) {
        loadingElement = document.createElement('div');
        loadingElement.id = 'loading-indicator';
        loadingElement.className = 'loading-overlay';
        loadingElement.innerHTML = `
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
            <p id="loading-message">${escapeHtml(message)}</p>
        `;
        document.body.appendChild(loadingElement);
    } else {
        document.getElementById('loading-message').textContent = message;
        loadingElement.style.display = 'flex';
    }
}

function hideLoading() {
    const loadingElement = document.getElementById('loading-indicator');
    if (loadingElement) {
        loadingElement.style.display = 'none';
    }
}

/**
 * Notification system functions
 */
function showMessage(message, type) {
    let messageContainer = document.getElementById('messages-container');
    
    if (!messageContainer) {
        messageContainer = document.createElement('div');
        messageContainer.id = 'messages-container';
        messageContainer.className = 'messages mb-3';
        messageContainer.setAttribute('role', 'alert');
        messageContainer.setAttribute('aria-live', 'polite');
        
        // Insert after heading when possible
        const heading = document.querySelector('h1') || document.querySelector('h2');
        if (heading && heading.parentNode) {
            heading.parentNode.insertBefore(messageContainer, heading.nextSibling);
        } else {
            // Fallback to main content
            const mainContent = document.querySelector('#main-content');
            if (mainContent) {
                mainContent.prepend(messageContainer);
            } else {
                document.body.prepend(messageContainer);
            }
        }
    }
    
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible fade show`;
    alert.innerHTML = `
        ${escapeHtml(message)}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    messageContainer.appendChild(alert);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (alert.parentNode) {
            alert.classList.remove('show');
            setTimeout(() => {
                if (alert.parentNode) {
                    alert.parentNode.removeChild(alert);
                }
            }, 150);
        }
    }, 5000);
}

// Message type helper functions
function showSuccess(message) {
    showMessage(message, 'success');
}

function showError(message) {
    showMessage(message, 'danger');
}

function showWarning(message) {
    showMessage(message, 'warning');
}

function showInfo(message) {
    showMessage(message, 'info');
}

/**
 * User authentication functions
 */
function showLoginPrompt(message) {
    const loginUrl = '/accounts/login/?next=' + encodeURIComponent(window.location.pathname);
    
    if (confirm(`${message}. Would you like to log in now?`)) {
        window.location.href = loginUrl;
    }
}

// Export all functions
export {
    // Loading indicators
    showLoading,
    hideLoading,
    
    // Authentication
    showLoginPrompt,
    
    // Notifications
    showMessage,
    showSuccess,
    showError,
    showWarning,
    showInfo
};