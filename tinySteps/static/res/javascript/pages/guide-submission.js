/**
 * Guide submission page functionality
 */

document.addEventListener('DOMContentLoaded', function() {
    initTagAccordion();
    initFormValidation();
});

/**
 * Initialize the tag accordion selection functionality
 */
function initTagAccordion() {
    const tagCheckboxes = document.querySelectorAll('.tag-checkbox');
    const selectedTagsContainer = document.getElementById('selectedTags');
    const hiddenTagInput = document.querySelector('.tag-hidden-input');
    
    if (!tagCheckboxes.length || !selectedTagsContainer || !hiddenTagInput) {
        return; // Required elements not found
    }
    
    // Parse any existing tags
    let selectedTags = [];
    if (hiddenTagInput.value) {
        selectedTags = hiddenTagInput.value.split(',').map(tag => tag.trim());
        updateSelectedTagsDisplay();
    }
    
    // Check any boxes that match existing tags
    tagCheckboxes.forEach(checkbox => {
        if (selectedTags.includes(checkbox.value)) {
            checkbox.checked = true;
        }
        
        checkbox.addEventListener('change', function() {
            if (this.checked) {
                // Add tag if not already in array
                if (!selectedTags.includes(this.value)) {
                    selectedTags.push(this.value);
                }
            } else {
                // Remove tag
                const index = selectedTags.indexOf(this.value);
                if (index > -1) {
                    selectedTags.splice(index, 1);
                }
            }
            
            // Update hidden input and display
            hiddenTagInput.value = selectedTags.join(', ');
            updateSelectedTagsDisplay();
        });
    });
    
    function updateSelectedTagsDisplay() {
        // Clear container
        selectedTagsContainer.innerHTML = '';
        
        // Show selected tags as badges
        if (selectedTags.length > 0) {
            const tagList = document.createElement('div');
            tagList.className = 'selected-tags-list d-flex flex-wrap gap-2';
            
            selectedTags.forEach(tag => {
                const badge = document.createElement('span');
                const isNutrition = document.querySelector('input[name="guide_type"]').value === 'nutrition';
                badge.className = `badge ${isNutrition ? 'bg-success' : 'bg-primary'} py-2 px-3`;
                badge.innerHTML = `${tag} <i class="fas fa-times ms-1 remove-tag" data-tag="${tag}"></i>`;
                tagList.appendChild(badge);
            });
            
            selectedTagsContainer.appendChild(tagList);
            
            // Add click handlers for tag removal
            document.querySelectorAll('.remove-tag').forEach(removeBtn => {
                removeBtn.addEventListener('click', function() {
                    const tagToRemove = this.dataset.tag;
                    
                    // Uncheck corresponding checkbox
                    tagCheckboxes.forEach(checkbox => {
                        if (checkbox.value === tagToRemove) {
                            checkbox.checked = false;
                        }
                    });
                    
                    // Remove from array
                    const index = selectedTags.indexOf(tagToRemove);
                    if (index > -1) {
                        selectedTags.splice(index, 1);
                    }
                    
                    // Update hidden input and display
                    hiddenTagInput.value = selectedTags.join(', ');
                    updateSelectedTagsDisplay();
                });
            });
        } else {
            selectedTagsContainer.innerHTML = '<p class="text-muted small">No tags selected</p>';
        }
    }
}

/**
 * Initialize form validation
 */
function initFormValidation() {
    const form = document.getElementById('guide-form');
    if (!form) return;
    
    const titleInput = document.getElementById('id_title');
    const contentInput = document.getElementById('id_desc');
    
    // Add validation feedback elements
    if (titleInput) {
        titleInput.addEventListener('input', function() {
            validateTitleField(this);
        });
        titleInput.addEventListener('blur', function() {
            validateTitleField(this);
        });
    }
    
    if (contentInput) {
        // For rich text editor compatibility
        const contentUpdateEvent = new CustomEvent('content-update');
        
        contentInput.addEventListener('input', function() {
            validateContentField(this);
        });
        contentInput.addEventListener('blur', function() {
            validateContentField(this);
        });
        // For rich text editors that may be in use
        document.addEventListener('content-update', function() {
            validateContentField(contentInput);
        });
        
        // Add character counter if it doesn't exist
        const fieldContainer = contentInput.closest('.mb-3');
        if (fieldContainer && !fieldContainer.querySelector('.character-counter')) {
            const counterElement = document.createElement('div');
            counterElement.className = 'character-counter small text-muted mt-1';
            fieldContainer.appendChild(counterElement);
            updateCharacterCount(contentInput, counterElement);
        }
    }
    
    // Form submission validation
    form.addEventListener('submit', function(e) {
        let isValid = true;
        
        if (titleInput && !validateTitleField(titleInput)) {
            isValid = false;
            titleInput.focus();
        }
        
        if (contentInput && !validateContentField(contentInput)) {
            isValid = false;
            if (isValid) contentInput.focus(); // Only focus if title was valid
        }
        
        if (!isValid) {
            e.preventDefault();
            
            // Show submission error message
            const errorAlert = document.createElement('div');
            errorAlert.className = 'alert alert-danger mt-3';
            errorAlert.innerHTML = '<i class="fas fa-exclamation-circle me-2"></i>Please fix the errors in the form before submitting.';
            errorAlert.setAttribute('role', 'alert');
            
            // Remove any existing error messages
            const existingAlert = form.querySelector('.alert-danger');
            if (existingAlert) existingAlert.remove();
            
            // Add the error message at the top of the form
            form.prepend(errorAlert);
            
            // Scroll to the top of the form
            errorAlert.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    });
    
    function validateTitleField(field) {
        const minLength = 5;
        const maxLength = 100;
        const value = field.value.trim();
        const isValid = value.length >= minLength && value.length <= maxLength;
        
        let errorMessage = '';
        if (value.length < minLength) {
            errorMessage = `Title must be at least ${minLength} characters long (currently ${value.length}).`;
        } else if (value.length > maxLength) {
            errorMessage = `Title must be at most ${maxLength} characters long (currently ${value.length}).`;
        }
        
        updateValidationFeedback(field, isValid, errorMessage);
        return isValid;
    }
    
    function validateContentField(field) {
        const minLength = 300;
        const maxLength = 2000;
        const value = field.value.trim();
        const isValid = value.length >= minLength && value.length <= maxLength;
        
        let errorMessage = '';
        if (value.length < minLength) {
            errorMessage = `Content must be at least ${minLength} characters long (currently ${value.length}).`;
        } else if (value.length > maxLength) {
            errorMessage = `Content must be at most ${maxLength} characters long (currently ${value.length}).`;
        }
        
        updateValidationFeedback(field, isValid, errorMessage);
        
        // Update character counter if it exists
        const fieldContainer = field.closest('.mb-3');
        if (fieldContainer) {
            const counterElement = fieldContainer.querySelector('.character-counter');
            if (counterElement) {
                updateCharacterCount(field, counterElement, minLength, maxLength);
            }
        }
        
        return isValid;
    }
    
    function updateValidationFeedback(field, isValid, errorMessage) {
        const fieldContainer = field.closest('.mb-3');
        if (!fieldContainer) return;
        
        // Remove existing feedback
        const existingFeedback = fieldContainer.querySelector('.invalid-feedback');
        if (existingFeedback) existingFeedback.remove();
        
        // Toggle validation classes
        field.classList.toggle('is-invalid', !isValid);
        field.classList.toggle('is-valid', isValid);
        
        // Add feedback message if invalid
        if (!isValid) {
            const feedbackElement = document.createElement('div');
            feedbackElement.className = 'invalid-feedback';
            feedbackElement.textContent = errorMessage;
            fieldContainer.appendChild(feedbackElement);
        }
    }
    
    function updateCharacterCount(field, counterElement, minLength = 300, maxLength = 2000) {
        const length = field.value.trim().length;
        
        counterElement.textContent = `${length} / ${minLength}-${maxLength} characters`;
        
        if (length < minLength) {
            counterElement.className = 'character-counter small text-danger mt-1';
        } else if (length > maxLength) {
            counterElement.className = 'character-counter small text-danger mt-1';
        } else {
            counterElement.className = 'character-counter small text-success mt-1';
        }
    }
}

export { initTagAccordion, initFormValidation };
