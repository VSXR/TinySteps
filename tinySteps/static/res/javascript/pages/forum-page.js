/**
 * Controller for the main forum page
 */
import { loadForumPosts, filterPosts } from '../features/forum.js';
import api from '../core/api.js';
import { showLoading, hideLoading, showSuccess, showError } from '../core/ui.js';

// Initialize the forum page
function initForumPage() {
    loadForumPosts();
    
    // Setup post creation form
    const postForm = document.getElementById('forum-post-form');
    if (postForm) {
        postForm.addEventListener('submit', handlePostSubmit);
    }
    
    // Setup category filter buttons
    const filterButtons = document.querySelectorAll('[data-filter]');
    if (filterButtons.length) {
        filterButtons.forEach(button => {
            button.addEventListener('click', function() {
                filterButtons.forEach(btn => btn.classList.remove('active'));
                this.classList.add('active');
                const filter = this.getAttribute('data-filter');
                filterPosts(filter);
            });
        });
    }
}

// Handle post form submission
async function handlePostSubmit(event) {
    event.preventDefault();
    const titleInput = document.getElementById('post-title');
    const contentInput = document.getElementById('post-content');
    
    if (!titleInput.value.trim() || !contentInput.value.trim()) {
        showError('Please fill in all required fields');
        return;
    }
    
    const data = {
        title: titleInput.value.trim(),
        content: contentInput.value.trim()
    };
    
    try {
        showLoading('Creating post...');
        const newPost = await api.createForumPost(data);

        titleInput.value = '';
        contentInput.value = '';
        
        const postsContainer = document.getElementById('forum-posts-container');
        if (postsContainer) {
            // Add new post to the top of the list if container exists
            const { createPostElement } = await import('../features/forum.js');
            const postElement = createPostElement(newPost);
            postsContainer.insertBefore(postElement, postsContainer.firstChild);
        } else {
            // Reload posts if container doesn't exist
            loadForumPosts();
        }
        
        hideLoading();
        showSuccess('Post created successfully');
    } catch (error) {
        hideLoading();
        showError('Failed to create post. Please try again later.');
        console.error('Error creating post:', error);
    }
}

// Run initialization when DOM is loaded
document.addEventListener('DOMContentLoaded', initForumPage);

export { initForumPage };