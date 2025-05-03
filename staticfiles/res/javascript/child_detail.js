/**
 * Main entry point for child detail page
 */
import { ChildDetailPage } from './pages/child-detail-page.js';

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', function() {
    try {
        const childDetailPage = new ChildDetailPage();
        childDetailPage.init();
        console.log('Child detail page functionality initialized');
    } catch (error) {
        console.error('Error initializing child detail page:', error);
    }
});