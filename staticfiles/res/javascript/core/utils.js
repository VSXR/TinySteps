/**
 * Security functions
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

/**
 * Authentication & CSRF functions
 */

// Get cookie by name
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

// get CSRF token from form input or cookies
function getCsrfToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]').value || getCookie('csrftoken');
}

// Check if user is authenticated
function isAuthenticated() {
    return document.body.classList.contains('user-authenticated');
}

export {
    escapeHtml,
    getCookie,
    getCsrfToken,
    isAuthenticated
};