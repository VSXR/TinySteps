/**
 * Guide submission page functionality
 */

document.addEventListener('DOMContentLoaded', function() {
    initTagAccordion();
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

export { initTagAccordion };