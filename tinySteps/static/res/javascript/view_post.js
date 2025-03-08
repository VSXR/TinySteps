document.addEventListener('DOMContentLoaded', () => {
    const urlPath = window.location.pathname;
    const postId = urlPath.split('/').pop();
    
    // SETTING THE EVENT LISTENERS FOR THE COMMENT FORM, LIKE BUTTON AND SHARE BUTTON
    // AND LOADING THE POST DETAILS AND COMMENTS
    if (postId && !isNaN(postId)) {
        loadPostDetails(postId);
        
        const commentForm = document.querySelector('form[action^="/parents_forum/add_comment"]');
        if (commentForm) {
            commentForm.addEventListener('submit', function(event) {
                event.preventDefault();
                handleCommentSubmit(event, postId);
            });
        }
        
        const likeButton = document.getElementById('like-button');
        if (likeButton) {
            likeButton.addEventListener('click', () => handleLikePost(postId));
        }
        
        const shareButton = document.getElementById('share-button');
        if (shareButton) {
            shareButton.addEventListener('click', () => handleSharePost(postId));
        }
    }
});

async function loadPostDetails(postId) {
    // TIMEOUT TO SHOW A MESSAGE IF THE POST ISN'T LOADED IN 5 SECONDS
    const timeoutId = setTimeout(() => {
        hideLoading();
        
        // IF THE CONTENT ELEMENT IS AVAILABLE, SHOW A MESSAGE,
        // OTHERWISE, THE PAGE WILL BE EMPTY
        const contentElement = document.querySelector('.post-content');
        if (contentElement) {
            contentElement.innerHTML = '<div class="alert alert-info text-center p-4" role="alert">' +
                '<i class="fa-solid fa-circle-info me-2"></i>' +
                'There isn\'t any posts available yet!' +
                '</div>';
        }
        
        // SET THE LIKE AND COMMENT COUNTERS TO 0
        const likeCountElement = document.getElementById('like-count');
        if (likeCountElement) {
            likeCountElement.textContent = '0';
        }
        
        const commentCountElement = document.querySelector('h2#comments-heading');
        if (commentCountElement) {
            commentCountElement.textContent = 'Comments (0)';
        }
        
        // SET THE COMMENT LIST TO A MESSAGE
        const commentListElement = document.querySelector('.comment-list');
        if (commentListElement) {
            const noCommentsElement = document.createElement('p');
            noCommentsElement.className = 'text-center my-4';
            noCommentsElement.textContent = 'No comments available.';
            commentListElement.parentNode.replaceChild(noCommentsElement, commentListElement);
        }
    }, 5000); // 5 seconds timeout

    // CANCEL THE TIMEOUT IF THE POST IS LOADED SUCCESSFULLY
    try {
        showLoading('Loading post details...');
        
        // LOAD THE POST DETAILS AND COMMENTS FROM THE API
        const post = await api.getForumPost(postId);
        clearTimeout(timeoutId); // Cancel timeout as data loaded successfully
        
        updatePostDetails(post);
        const comments = await api.getForumPostComments(postId);
        displayComments(comments);
        
        hideLoading();
    } catch (error) {
        clearTimeout(timeoutId); // Cancel timeout as we have a specific error
        
        hideLoading();
        showError('Failed to load post. Please try again later.');
        console.error('Error loading post:', error);
    }
}

function updatePostDetails(post) {
    // Update post title
    const titleElement = document.querySelector('h1.fs-4');
    if (titleElement) titleElement.textContent = post.title;
    
    // Update post content
    const contentElement = document.querySelector('.post-content');
    if (contentElement) {
        contentElement.innerHTML = post.content.replace(/\n/g, '<br>');
    }
    
    // Update author and date
    const authorElement = document.querySelector('.post-author');
    if (authorElement) {
        authorElement.innerHTML = `<span class="fw-bold">Posted by:</span> ${escapeHtml(post.author.username)}`;
    }
    
    const dateElement = document.querySelector('.post-date time');
    if (dateElement) {
        const postDate = new Date(post.created_at);
        dateElement.setAttribute('datetime', postDate.toISOString().split('T')[0]);
        dateElement.textContent = postDate.toLocaleDateString('en-US', { 
            year: 'numeric', month: 'long', day: 'numeric' 
        });
    }
    
    // UPDATING THE LIKE COUNTER
    const likeCountElement = document.getElementById('like-count');
    if (likeCountElement) {
        likeCountElement.textContent = post.likes_count || 0;
    }
    
    // UPDATING THE COMMENT COUNTER
    const commentCountElement = document.querySelector('h2#comments-heading');
    if (commentCountElement) {
        commentCountElement.textContent = `Comments (${post.comments_count || 0})`;
    }
    
    // UPDATING THE TAGS LIST (IF IS AVAILABLE)
    if (post.tags && post.tags.length > 0) {
        const tagsContainer = document.querySelector('.post-tags');
        if (tagsContainer) {
            tagsContainer.innerHTML = '<h2 id="post-categories" class="visually-hidden">Post Categories</h2>';
            post.tags.forEach(tag => {
                const tagLink = document.createElement('a');
                tagLink.href = `/parents_forum/?tag=${encodeURIComponent(tag.slug)}`;
                tagLink.className = 'badge bg-primary text-decoration-none me-1 mb-1';
                tagLink.textContent = `#${tag.name}`;
                tagsContainer.appendChild(tagLink);
            });
        }
    }
    
    // UPDATING THE PAGE TITLE
    document.title = `${post.title} - TINY STEPS FORUM`;
}

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

async function handleCommentSubmit(event, postId) {
    const form = event.target;
    const commentContent = form.querySelector('textarea[name="content"]').value;
    
    if (!commentContent.trim()) {
        showError('Comment text is required.');
        return;
    }
    
    try {
        showLoading('Posting your comment...');
        const response = await api.addForumComment(postId, commentContent);
        
        // CLEARING THE FORM AND DISPLAYING THE NEW COMMENT ONE BY ONE
        form.reset();
        const comments = await api.getForumPostComments(postId);
        displayComments(comments);
        
        hideLoading();
        showSuccess('Comment posted successfully!');
        
        // SCROLLS TO THE COMMENTS SECTION AFTER POSTING
        const commentsHeading = document.getElementById('comments-heading');
        if (commentsHeading) {
            commentsHeading.scrollIntoView({ behavior: 'smooth' });
        }
    } catch (error) {
        hideLoading();
        showError('Failed to post your comment. Please try again.');
        console.error('Error posting comment:', error);
    }
}

// Replace the existing handleLikePost function
async function handleLikePost(postId) {
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
    } catch (error) {
        hideLoading();
        showError('Failed to process your like. Please try again.');
        console.error('Error liking post:', error);
    }
}

function handleSharePost(postId) {
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

function isAuthenticated() {
    // Check if user is authenticated (this is a simple example)
    // In a real app, you might have this information in a global state or check with the API
    return document.body.classList.contains('user-authenticated');
}

function showLoginPrompt(message) {
    const loginUrl = '/accounts/login/?next=' + encodeURIComponent(window.location.pathname);
    
    if (confirm(`${message}. Would you like to log in now?`)) {
        window.location.href = loginUrl;
    }
}

function showLoading(message = 'Loading...') {
    let loadingElement = document.getElementById('loading-indicator');
    
    if (!loadingElement) {
        loadingElement = document.createElement('div');
        loadingElement.id = 'loading-indicator';
        loadingElement.className = 'loading-overlay';
        loadingElement.innerHTML = `
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
            <p id="loading-message">${escapeHtml(message)}</p>
        `;
        document.body.appendChild(loadingElement);
    } else {
        document.getElementById('loading-message').textContent = message;
        loadingElement.style.display = 'flex';
    }
}

function hideLoading() {
    const loadingElement = document.getElementById('loading-indicator');
    if (loadingElement) {
        loadingElement.style.display = 'none';
    }
}

function showSuccess(message) {
    showMessage(message, 'success');
}

function showError(message) {
    showMessage(message, 'danger');
}

function showMessage(message, type) {
    let messageContainer = document.getElementById('messages-container');
    
    if (!messageContainer) {
        messageContainer = document.createElement('div');
        messageContainer.id = 'messages-container';
        messageContainer.className = 'messages mb-3';
        messageContainer.setAttribute('role', 'alert');
        messageContainer.setAttribute('aria-live', 'polite');
        
        // Insert it after the heading
        const heading = document.querySelector('h1') || document.querySelector('h2');
        if (heading && heading.parentNode) {
            heading.parentNode.insertBefore(messageContainer, heading.nextSibling);
        } else {
            // Fallback to prepending to main content
            const mainContent = document.querySelector('#main-content');
            if (mainContent) {
                mainContent.prepend(messageContainer);
            } else {
                // Last resort - add to body
                document.body.prepend(messageContainer);
            }
        }
    }
    
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible fade show`;
    alert.innerHTML = `
        ${escapeHtml(message)}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    messageContainer.appendChild(alert);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (alert.parentNode) {
            alert.classList.remove('show');
            setTimeout(() => {
                if (alert.parentNode) {
                    alert.parentNode.removeChild(alert);
                }
            }, 150);
        }
    }, 5000);
}

// HELPER TO PREVENT XSS ATTACKS
function escapeHtml(unsafe) {
    if (unsafe === null || unsafe === undefined) return '';
    
    return unsafe
        .toString()
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}