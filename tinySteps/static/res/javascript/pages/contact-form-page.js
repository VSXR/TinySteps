document.addEventListener('DOMContentLoaded', function() {
    // Add floating label animation
    const formControls = document.querySelectorAll('.form-control');
    formControls.forEach(control => {
        // Initial state check
        if (control.value) {
            control.parentElement.classList.add('is-filled');
        }
        
        // Event listeners
        control.addEventListener('focus', function() {
            this.parentElement.classList.add('is-focused');
        });
        
        control.addEventListener('blur', function() {
            this.parentElement.classList.remove('is-focused');
            if (this.value) {
                this.parentElement.classList.add('is-filled');
            } else {
                this.parentElement.classList.remove('is-filled');
            }
        });
    });
    
    // Form validation feedback with accessibility support
    const contactForm = document.getElementById('contactForm');
    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            if (!this.checkValidity()) {
                e.preventDefault();
                e.stopPropagation();
                
                // Announce validation errors to screen readers
                const firstInvalid = this.querySelector(':invalid');
                if (firstInvalid) {
                    firstInvalid.focus();
                    const errorMessage = document.createElement('div');
                    errorMessage.setAttribute('role', 'alert');
                    errorMessage.setAttribute('aria-live', 'assertive');
                    errorMessage.classList.add('visually-hidden');
                    errorMessage.textContent = 'Please correct the errors in the form';
                    this.appendChild(errorMessage);
                    setTimeout(() => errorMessage.remove(), 3000);
                }
            }
            this.classList.add('was-validated');
        });
        
        // Add ARIA labels to form fields dynamically
        const formFields = contactForm.querySelectorAll('.form-control');
        formFields.forEach(field => {
            const label = field.closest('.form-group').querySelector('label');
            if (label) {
                const labelText = label.textContent.trim();
                if (labelText) {
                    field.setAttribute('aria-label', labelText);
                }
            }
        });
    }
    
    // Announce screen reader messages
    const messages = document.querySelectorAll('.alert');
    if (messages.length > 0) {
        setTimeout(() => {
            messages.forEach(message => {
                if (message.classList.contains('alert-success')) {
                    message.setAttribute('role', 'status');
                }
            });
        }, 1000);
    }
    
    // Enhance accordion accessibility
    const accordionButtons = document.querySelectorAll('.accordion-button');
    accordionButtons.forEach(button => {
        button.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                this.click();
            }
        });
    });
});