/**
 * User interactions: likes, sharing
 */
import api from '../core/api.js';
import { isAuthenticated } from '../core/utils.js';
import { showLoading, hideLoading, showSuccess, showError, showLoginPrompt } from '../core/ui.js';

// Handle post liking
async function likePost(postId) {
    if (!isAuthenticated()) {
        showLoginPrompt('Please log in to like this post');
        return;
    }
    
    try {
        showLoading('Processing...');
        const response = await api.likeForumPost(postId);
        hideLoading();
        
        // Update the like count in the UI
        const likeCount = document.getElementById('like-count');
        if (likeCount && response && response.likes_count !== undefined) {
            likeCount.textContent = response.likes_count;
        }
        
        // Update button appearance based on liked state
        const likeButton = document.getElementById('like-button');
        if (likeButton && response && response.liked !== undefined) {
            if (response.liked) {
                likeButton.classList.add('liked', 'btn-primary');
                likeButton.classList.remove('btn-outline-primary');
                likeButton.setAttribute('aria-pressed', 'true');
                showSuccess('Post liked!');
            } else {
                likeButton.classList.remove('liked', 'btn-primary');
                likeButton.classList.add('btn-outline-primary');
                likeButton.setAttribute('aria-pressed', 'false');
                showSuccess('Post unliked');
            }
        }
        
        return response;
    } catch (error) {
        hideLoading();
        showError('Failed to process your like. Please try again.');
        console.error('Error liking post:', error);
        throw error;
    }
}

// Handle post sharing
function sharePost(postId) {
    const shareUrl = window.location.origin + `/parents_forum/view/${postId}`;
    
    // Check if Web Share API is available
    if (navigator.share) {
        navigator.share({
            title: document.title,
            url: shareUrl
        }).catch(error => {
            console.error('Error sharing:', error);
            showFallbackShareUI(shareUrl);
        });
    } else {
        showFallbackShareUI(shareUrl);
    }
}

// Fallback sharing when Web Share API isn't available
function showFallbackShareUI(url) {
    // Copy URL to clipboard
    navigator.clipboard.writeText(url)
        .then(() => {
            showSuccess('Link copied to clipboard!');
        })
        .catch(() => {
            // Show a modal/popup with the URL to copy manually
            prompt('Copy this link to share the post:', url);
        });
}

// Initialize like buttons on the page
function setupLikeButtons() {
    document.querySelectorAll('.like-button').forEach(button => {
        if (button.dataset.initialized === 'true') return;
        
        button.dataset.initialized = 'true';
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            const postId = this.closest('[data-post-id]')?.dataset.postId || 
                           window.location.pathname.split('/').filter(Boolean).pop();
                           
            if (postId) {
                likePost(postId);
            }
        });
    });
}

export {
    likePost,
    sharePost,
    showFallbackShareUI,
    setupLikeButtons
};