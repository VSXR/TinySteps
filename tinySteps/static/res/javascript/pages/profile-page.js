/**
 * Profile page functionality
 * Handles card interactions, button alignment and accessibility enhancements
 */
document.addEventListener('DOMContentLoaded', function() {
    // Add hover effects to cards with element-elevation class
    const cards = document.querySelectorAll('.element-elevation');
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.classList.add('shadow');
            this.style.transform = 'translateY(-5px)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.classList.remove('shadow');
            this.style.transform = 'translateY(0)';
        });
    });
    
    // Ensure all buttons within cards are properly centered
    const cardButtons = document.querySelectorAll('.card-body .btn, .card-footer .btn');
    cardButtons.forEach(button => {
        // Add display flex and center alignment classes if not present
        if (!button.classList.contains('d-flex') && !button.classList.contains('d-inline-flex')) {
            button.classList.add('d-flex', 'align-items-center', 'justify-content-center');
        }
    });
    
    // Special handling for header buttons that need to be centered
    const headerButtons = document.querySelectorAll('#children-section-header .btn, #forum-activity-header .btn');
    headerButtons.forEach(button => {
        button.classList.add('d-inline-flex', 'align-items-center', 'justify-content-center');
        // Ensure they're not pushed to edges in mobile
        if (window.innerWidth < 576) {
            button.style.marginTop = '0.5rem';
            button.style.marginLeft = 'auto';
            button.style.marginRight = 'auto';
            button.style.display = 'flex';
        }
    });
    
    // Fix button alignment in small screens
    function adjustButtonsForScreenSize() {
        const isSmallScreen = window.innerWidth < 576;
        const actionButtons = document.querySelectorAll('.card-body .btn-outline-primary, .card-body .btn-primary');
        const headerButtons = document.querySelectorAll('#children-section-header .btn, #forum-activity-header .btn');
        
        actionButtons.forEach(button => {
            if (isSmallScreen) {
                button.classList.add('w-100', 'mb-2');
            } else {
                button.classList.remove('w-100', 'mb-2');
            }
        });
        
        // Adjust header buttons in mobile view
        headerButtons.forEach(button => {
            if (isSmallScreen) {
                button.style.marginTop = '0.5rem';
                button.style.marginLeft = 'auto';
                button.style.marginRight = 'auto';
                button.style.display = 'flex';
            } else {
                button.style.marginTop = '';
                button.style.marginLeft = '';
                button.style.marginRight = '';
                button.style.display = '';
            }
        });

        // Ajustar párrafos en tarjetas recomendadas
        const recommendedCards = document.querySelectorAll('.element-elevation .card-body p');
        recommendedCards.forEach(paragraph => {
            if (isSmallScreen) {
                paragraph.style.minHeight = '0';
                paragraph.style.height = 'auto';
            } else {
                paragraph.style.minHeight = '';
                paragraph.style.height = '';
            }
        });
    }
    
    // Run initially and on window resize
    adjustButtonsForScreenSize();
    window.addEventListener('resize', adjustButtonsForScreenSize);
    
    // Ensure settings links are properly aligned
    const settingsLinks = document.querySelectorAll('[aria-labelledby="account-settings-header"] a');
    settingsLinks.forEach(link => {
        link.style.display = 'flex';
        link.style.alignItems = 'center';
        
        // Ensure consistent height and spacing
        const textContainer = link.querySelector('.flex-grow-1');
        if (textContainer) {
            textContainer.style.minHeight = '50px';
            textContainer.style.display = 'flex';
            textContainer.style.flexDirection = 'column';
            textContainer.style.justifyContent = 'center';
        }
    });
    
    // Ensure equal height for recommendation cards
    function matchRecommendationCardHeights() {
        const recommendationCards = document.querySelectorAll('.card-body .card.element-elevation');
        const recommendedParagraphs = document.querySelectorAll('.element-elevation .card-body p');
        
        if (recommendationCards.length > 0 && window.innerWidth >= 768) {
            // Reset heights first
            recommendationCards.forEach(card => {
                card.style.height = '';
            });
            
            recommendedParagraphs.forEach(p => {
                p.style.height = '';
            });
            
            // Calculate max height for paragraphs
            let maxTextHeight = 0;
            recommendedParagraphs.forEach(p => {
                maxTextHeight = Math.max(maxTextHeight, p.offsetHeight);
            });
            
            // Apply max height to paragraphs
            if (maxTextHeight > 0) {
                recommendedParagraphs.forEach(p => {
                    p.style.height = maxTextHeight + 'px';
                });
            }
            
            // Calculate max height for cards
            let maxCardHeight = 0;
            recommendationCards.forEach(card => {
                maxCardHeight = Math.max(maxCardHeight, card.offsetHeight);
            });
            
            // Apply max height to cards
            recommendationCards.forEach(card => {
                card.style.height = maxCardHeight + 'px';
            });
        }
    }
    
    // Match account settings card heights
    function matchSettingsCardHeights() {
        const settingsCards = document.querySelectorAll('[aria-labelledby="account-settings-header"] [role="listitem"]');
        if (settingsCards.length > 0 && window.innerWidth >= 768) {
            // Reset heights first
            settingsCards.forEach(card => {
                card.querySelector('a').style.height = '';
            });
            
            // Calculate max height
            let maxHeight = 0;
            settingsCards.forEach(card => {
                const cardHeight = card.querySelector('a').offsetHeight;
                maxHeight = Math.max(maxHeight, cardHeight);
            });
            
            // Apply max height
            settingsCards.forEach(card => {
                card.querySelector('a').style.height = maxHeight + 'px';
            });
        }
    }
    
    // Run after a slight delay to ensure all content is loaded
    setTimeout(function() {
        matchRecommendationCardHeights();
        matchSettingsCardHeights();
    }, 100);
    
    window.addEventListener('resize', function() {
        matchRecommendationCardHeights();
        matchSettingsCardHeights();
    });
    
    // Add accessibility improvements for screen readers
    const messages = document.querySelectorAll('.alert');
    if (messages.length > 0) {
        const messageContainer = document.getElementById('messages-container');
        if (messageContainer) {
            setTimeout(() => {
                messages.forEach(message => {
                    if (message.classList.contains('alert-success')) {
                        message.setAttribute('role', 'status');
                    }
                });
            }, 1000);
        }
    }
});