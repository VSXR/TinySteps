/**
 * Comment functionality for forum posts
 */
import api from '../core/api.js';
import { escapeHtml } from '../core/utils.js';
import { showLoading, hideLoading, showSuccess, showError } from '../core/ui.js';

// Load and display comments
async function loadComments(postId) {
    try {
        const comments = await api.getForumPostComments(postId);
        displayComments(comments);
        return comments;
    } catch (error) {
        console.error('Error loading comments:', error);
        showError('Failed to load comments. Please try again later.');
        throw error;
    }
}

// Display comments in the UI
function displayComments(comments) {
    const commentListElement = document.querySelector('.comment-list');
    if (!commentListElement) return;
    
    if (comments.length === 0) {
        const noCommentsElement = document.createElement('p');
        noCommentsElement.className = 'text-center my-4';
        noCommentsElement.textContent = 'No comments yet. Be the first to comment!';
        commentListElement.parentNode.replaceChild(noCommentsElement, commentListElement);
        return;
    }
    
    commentListElement.innerHTML = '';
    comments.forEach(comment => {
        const commentElement = createCommentElement(comment);
        commentListElement.appendChild(commentElement);
    });
}

// Create comment element
function createCommentElement(comment) {
    const commentDiv = document.createElement('div');
    commentDiv.className = 'card mb-3';
    commentDiv.id = `comment-${comment.id}`;
    
    const commentDate = new Date(comment.created_at);
    const formattedDate = commentDate.toLocaleDateString('en-US', {
        year: 'numeric', month: 'short', day: 'numeric'
    });
    
    commentDiv.innerHTML = `
        <div class="card-body">
            <div class="d-flex justify-content-between mb-2">
                <div>
                    <strong>${escapeHtml(comment.author.username)}</strong>
                </div>
                <time datetime="${commentDate.toISOString().split('T')[0]}" class="text-muted">
                    ${formattedDate}
                </time>
            </div>
            <p>${escapeHtml(comment.text)}</p>
        </div>
    `;
    
    return commentDiv;
}

// Add a new comment
async function addComment(postId, commentText) {
    if (!commentText.trim()) {
        showError('Comment text is required.');
        return;
    }
    
    try {
        showLoading('Posting your comment...');
        await api.addForumComment(postId, commentText);
        
        // Reload comments to show the new one
        const comments = await api.getForumPostComments(postId);
        displayComments(comments);
        
        hideLoading();
        showSuccess('Comment posted successfully!');
        
        // Scroll to the comments section
        const commentsHeading = document.getElementById('comments-heading');
        if (commentsHeading) {
            commentsHeading.scrollIntoView({ behavior: 'smooth' });
        }
        
        return true;
    } catch (error) {
        hideLoading();
        showError('Failed to post your comment. Please try again.');
        console.error('Error posting comment:', error);
        return false;
    }
}

// Setup comment form submission
function setupCommentForm() {
    const commentForm = document.querySelector('form[action*="add_comment"]');
    if (!commentForm) return;
    
    commentForm.addEventListener('submit', async function(event) {
        event.preventDefault();
        
        const postId = window.location.pathname.split('/').filter(Boolean).pop();
        const commentContent = this.querySelector('textarea[name="content"]').value;
        
        const success = await addComment(postId, commentContent);
        if (success) {
            this.reset();
        }
    });
}

export {
    loadComments,
    displayComments,
    createCommentElement,
    addComment,
    setupCommentForm
};