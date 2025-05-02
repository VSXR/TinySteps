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
        if (!button.classList.contains('d-flex')) {
            button.classList.add('d-flex', 'align-items-center', 'justify-content-center');
        }
    });
    
    // Fix button alignment in small screens
    function adjustButtonsForScreenSize() {
        const isSmallScreen = window.innerWidth < 576;
        const actionButtons = document.querySelectorAll('.card-body .btn-outline-primary, .card-body .btn-primary');
        
        actionButtons.forEach(button => {
            if (isSmallScreen) {
                button.classList.add('w-100', 'mb-2');
            } else {
                button.classList.remove('w-100', 'mb-2');
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