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

// Function to add a comment and update the UI
async function addComment(postId, text) {
    showLoading('Posting comment...');
    
    try {
        const response = await fetch(commentForm.action, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: new URLSearchParams({
                'content': text
            })
        });
        
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        
        // Refresh page to show new comment
        window.location.reload();
    } catch (error) {
        hideLoading();
        showError('Failed to post comment. Please try again.');
        throw error;
    }
}

// Setup comment form submission
function setupCommentForm() {
    const commentForm = document.getElementById('comment-form');
    if (!commentForm) return;
    
    commentForm.addEventListener('submit', async function(event) {
        event.preventDefault();
        
        const commentContent = document.getElementById('comment-content').value.trim();
        if (!commentContent) {
            showError('Please enter a comment');
            return;
        }
        
        const postId = window.location.pathname.split('/').filter(Boolean)[2]; // Extract post ID from URL
        
        try {
            await addComment(postId, commentContent);
            this.reset(); // Clear the form
        } catch (error) {
            console.error("Error adding comment:", error);
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