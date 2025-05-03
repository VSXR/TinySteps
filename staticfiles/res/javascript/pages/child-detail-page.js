/**
 * Child detail page functionality
 * Handles tab interactions and visual effects
 */

class ChildDetailPage {
    constructor() {
        this.tabs = document.querySelectorAll('.nav-tabs .nav-link');
        this.tabElements = document.querySelectorAll('[data-bs-toggle="tab"]');
    }

    init() {
        this.enhanceTabsAccessibility();
        this.setupTabContentAnimation();
    }

    /**
     * Enhance tabs accessibility with title attributes
     */
    enhanceTabsAccessibility() {
        this.tabs.forEach(tab => {
            tab.addEventListener('mouseover', function() {
                if (!this.classList.contains('active')) {
                    this.setAttribute('title', 'Click to view ' + this.textContent.trim());
                }
            });
        });
    }

    /**
     * Add animation effect when switching tabs
     */
    setupTabContentAnimation() {
        this.tabElements.forEach(tab => {
            tab.addEventListener('shown.bs.tab', function(e) {
                const target = document.querySelector(e.target.getAttribute('data-bs-target'));
                if (target) {
                    target.style.animation = 'fadeIn 0.3s';
                    setTimeout(() => {
                        target.style.animation = '';
                    }, 300);
                }
            });
        });
    }
}

// Export the class
export { ChildDetailPage };