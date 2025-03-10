/**
 * Core utility functions used across the application
 */

// Prevent XSS attacks by escaping HTML
function escapeHtml(unsafe) {
    if (unsafe === null || unsafe === undefined) return '';
    
    return unsafe
        .toString()
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

// Get CSRF token from cookies
function getCsrfToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]').value || getCookie('csrftoken');
}

// Get cookie by name (for CSRF token)
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Check if user is authenticated
function isAuthenticated() {
    return document.body.classList.contains('user-authenticated');
}

export {
    escapeHtml,
    getCsrfToken,
    getCookie,
    isAuthenticated
};