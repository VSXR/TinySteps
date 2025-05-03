import { ChildrenListPage } from './pages/child-list-page.js';

document.addEventListener('DOMContentLoaded', function() {
    try {
        const childrenListPage = new ChildrenListPage();
        childrenListPage.init();
        console.log('Children list page functionality initialized');
    } catch (error) {
        console.error('Error initializing children list page:', error);
    }
});