/**
 * Children list page functionality
 * Handles card animations, search, filtering, view toggling and statistics
 */
class ChildrenListPage {
    constructor() {
        // Core elements
        this.childCards = document.querySelectorAll('.child-card');
        this.childItems = document.querySelectorAll('[role="listitem"]');
        this.searchInput = document.querySelector('#search-children');
        this.filterButtons = document.querySelectorAll('.filter-btn');
        
        // View toggle buttons
        this.cardViewBtn = document.querySelector('[aria-label="Card view"]');
        this.listViewBtn = document.querySelector('[aria-label="List view"]');
        this.childrenContainer = document.querySelector('[role="list"]');
        
        // Stats elements
        this.totalChildrenCount = document.querySelector('#total-children-count');
        this.vaccinesCount = document.querySelector('#vaccines-count');
        this.upcomingEventsCount = document.querySelector('#upcoming-events-count');
        this.milestonesCount = document.querySelector('#recent-milestones-count');
        
        // Current view state
        this.currentView = 'card';
        
        // Search timeout for debouncing
        this.searchTimeout = null;
    }

    init() {
        this.setupCardAnimations();
        this.setupHoverEffects();
        this.setupSearch();
        this.setupFilters();
        this.setupViewToggle();
        this.loadStatistics();
        this.forceShowCards();
        
        console.log("Children list page functionality initialized");
    }

    /**
     * Set up staggered fade-in animations for child cards
     */
    setupCardAnimations() {
        this.childItems.forEach((item, index) => {
            setTimeout(() => {
                item.style.opacity = '0';
                item.style.animation = 'fadeInUp 0.5s ease forwards';
                item.style.opacity = '1';
            }, index * 100);
        });
    }

    /**
     * Add hover effects to child cards
     */
    setupHoverEffects() {
        this.childCards.forEach(card => {
            card.addEventListener('mouseenter', function() {
                this.classList.add('shadow-lg');
                this.style.transform = 'translateY(-5px)';
            });
            card.addEventListener('mouseleave', function() {
                this.classList.remove('shadow-lg');
                this.classList.add('shadow-sm');
                this.style.transform = 'translateY(0)';
            });
        });
    }

    /**
     * Setup search functionality with debouncing
     */
    setupSearch() {
        if (!this.searchInput) return;
        
        this.searchInput.addEventListener('input', () => {
            const searchTerm = this.searchInput.value.toLowerCase().trim();
            
            // Clear any previous timeout
            if (this.searchTimeout) {
                clearTimeout(this.searchTimeout);
            }
            
            // Set a timeout to debounce the search
            this.searchTimeout = setTimeout(() => {
                if (searchTerm.length >= 2 || searchTerm.length === 0) {
                    this.performSearch(searchTerm);
                }
            }, 300);
        });

        // Handle the form submission
        const searchForm = this.searchInput.closest('form');
        if (searchForm) {
            searchForm.addEventListener('submit', (e) => {
                e.preventDefault();
                const searchTerm = this.searchInput.value.toLowerCase().trim();
                if (searchTerm.length >= 2 || searchTerm.length === 0) {
                    this.performSearch(searchTerm);
                }
            });
        }
    }
    
    /**
     * Perform AJAX search for children
     */
    performSearch(searchTerm) {
        // Show a loading indicator
        this.showSearchLoading();
        
        // Get the current URL and add search parameter
        const url = new URL(window.location.href);
        url.searchParams.set('search', searchTerm);
        
        // Reset to page 1 for new searches
        url.searchParams.set('page', '1');
        
        // Update URL without reloading
        window.history.pushState({}, '', url);
        
        // Fetch results via AJAX
        fetch(url, {
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.text();
        })
        .then(html => {
            // Parse the HTML response
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');
            
            // Replace the children list
            const newChildrenContainer = doc.querySelector('[role="list"]');
            if (newChildrenContainer) {
                this.childrenContainer.innerHTML = newChildrenContainer.innerHTML;
                
                // Re-initialize elements
                this.childCards = document.querySelectorAll('.child-card');
                this.childItems = document.querySelectorAll('[role="listitem"]');
                
                // Re-apply effects
                this.setupCardAnimations();
                this.setupHoverEffects();
                
                // Update pagination if it exists
                const newPagination = doc.querySelector('.pagination');
                const currentPagination = document.querySelector('.pagination');
                if (newPagination && currentPagination) {
                    currentPagination.innerHTML = newPagination.innerHTML;
                }
                
                // Apply current view mode
                this.applyCurrentView();
            }
            
            // Hide loading indicator
            this.hideSearchLoading();
            
            // Force show cards after ajax update
            this.forceShowCards();
        })
        .catch(error => {
            console.error('Search error:', error);
            this.hideSearchLoading();
            
            // Fallback to client-side filtering
            this.filterChildrenByName(searchTerm);
        });
    }
    
    /**
     * Fallback client-side filtering by name
     */
    filterChildrenByName(searchTerm) {
        this.childCards.forEach(card => {
            const childNameElement = card.querySelector('.child-name');
            if (!childNameElement) return;
            
            const childName = childNameElement.textContent.toLowerCase();
            const listItem = card.closest('[role="listitem"]');
            
            if (childName.includes(searchTerm) || searchTerm === '') {
                listItem.style.display = '';
            } else {
                listItem.style.display = 'none';
            }
        });
    }
    
    /**
     * Show search loading indicator
     */
    showSearchLoading() {
        const searchContainer = this.searchInput.closest('.input-group');
        if (!searchContainer.querySelector('.search-spinner')) {
            const spinner = document.createElement('div');
            spinner.className = 'search-spinner position-absolute end-0 top-50 translate-middle-y me-3';
            spinner.innerHTML = '<div class="spinner-border spinner-border-sm text-primary" role="status"><span class="visually-hidden">Loading...</span></div>';
            searchContainer.style.position = 'relative';
            searchContainer.appendChild(spinner);
        }
    }
    
    /**
     * Hide search loading indicator
     */
    hideSearchLoading() {
        const searchContainer = this.searchInput.closest('.input-group');
        const spinner = searchContainer.querySelector('.search-spinner');
        if (spinner) {
            spinner.remove();
        }
    }

    /**
     * Setup filter buttons (all, infants, toddlers)
     */
    setupFilters() {
        if (!this.filterButtons.length) return;
        
        this.filterButtons.forEach(button => {
            button.addEventListener('click', () => {
                // Update active state
                this.filterButtons.forEach(btn => btn.classList.remove('active'));
                button.classList.add('active');
                
                // Apply filter
                const filter = button.dataset.filter;
                this.filterChildren(filter);
            });
        });
    }
    
    /**
     * Filter children based on selected filter
     */
    filterChildren(filter) {
        if (filter === 'all') {
            this.childItems.forEach(item => {
                item.style.display = '';
            });
            return;
        }
        
        this.childItems.forEach(item => {
            const card = item.querySelector('.child-card');
            if (!card) return;
            
            const ageMonths = parseInt(card.dataset.age || '0');
            if ((filter === 'infants' && ageMonths < 12) || 
                (filter === 'toddlers' && ageMonths >= 12 && ageMonths < 36)) {
                item.style.display = '';
            } else {
                item.style.display = 'none';
            }
        });
    }
    
    /**
     * Setup view toggle (card/list view)
     */
    setupViewToggle() {
        if (!this.cardViewBtn || !this.listViewBtn) return;
        
        this.cardViewBtn.addEventListener('click', () => {
            this.setView('card');
        });
        
        this.listViewBtn.addEventListener('click', () => {
            this.setView('list');
        });
    }
    
    /**
     * Set current view mode and update UI
     */
    setView(viewMode) {
        this.currentView = viewMode;
        
        // Update active button state
        if (viewMode === 'card') {
            this.cardViewBtn.classList.add('active');
            this.listViewBtn.classList.remove('active');
        } else {
            this.cardViewBtn.classList.remove('active');
            this.listViewBtn.classList.add('active');
        }
        
        this.applyCurrentView();
    }
    
    /**
     * Apply current view mode to DOM
     */
    applyCurrentView() {
        if (!this.childrenContainer) return;
        
        if (this.currentView === 'card') {
            this.childrenContainer.classList.remove('list-view');
            this.childrenContainer.classList.add('card-view');
            
            this.childItems.forEach(item => {
                item.classList.remove('col-12', 'mb-3');
                item.classList.add('col-md-6', 'col-lg-4', 'col-xl-3');
            });
        } else {
            this.childrenContainer.classList.remove('card-view');
            this.childrenContainer.classList.add('list-view');
            
            this.childItems.forEach(item => {
                item.classList.remove('col-md-6', 'col-lg-4', 'col-xl-3');
                item.classList.add('col-12', 'mb-3');
                
                // Reset shadow when in list view
                const card = item.querySelector('.card');
                if (card) {
                    card.classList.remove('shadow-lg');
                    card.classList.add('shadow-sm');
                }
            });
        }
    }
    
    /**
     * Force show all cards - ensures all cards are visible
     */
    forceShowCards() {
        setTimeout(() => {
            const childCards = document.querySelectorAll('.child-card');
            childCards.forEach(card => {
                card.style.display = 'block';
                card.style.opacity = '1';
                card.style.animation = 'none';
            });
        }, 100);
    }
    
    /**
     * Load statistics from API
     */
    loadStatistics() {
        // Only proceed if counter elements exist
        if (!this.totalChildrenCount && !this.vaccinesCount && 
            !this.upcomingEventsCount && !this.milestonesCount) return;
            
        // Get current counts from HTML as fallback values
        const currentTotalCount = this.totalChildrenCount ? this.totalChildrenCount.textContent : '0';
        const currentVaccinesCount = this.vaccinesCount ? this.vaccinesCount.textContent : '0';
        const currentEventsCount = this.upcomingEventsCount ? this.upcomingEventsCount.textContent : '0';
        const currentMilestonesCount = this.milestonesCount ? this.milestonesCount.textContent : '0';
            
        // Fetch statistics from server
        fetch('/children/statistics/', {
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value || ''
            },
            credentials: 'same-origin'
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            // Update counter elements
            if (this.totalChildrenCount) {
                this.totalChildrenCount.textContent = data.total_children || currentTotalCount;
            }
            
            if (this.vaccinesCount) {
                this.vaccinesCount.textContent = data.vaccines_up_to_date || currentVaccinesCount;
            }
            
            if (this.upcomingEventsCount) {
                this.upcomingEventsCount.textContent = data.upcoming_events || currentEventsCount;
            }
            
            if (this.milestonesCount) {
                this.milestonesCount.textContent = data.recent_milestones || currentMilestonesCount;
            }
        })
        .catch(error => {
            console.error('Error loading statistics:', error);
        });
    }
}

export { ChildrenListPage };