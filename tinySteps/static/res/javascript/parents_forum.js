document.addEventListener('DOMContentLoaded', () => {
    loadParentsForumPosts();
    
    const postForm = document.getElementById('forum-post-form');
    if (postForm) {
        postForm.addEventListener('submit', handlePostSubmit);
    }
    
    const filterButtons = document.querySelectorAll('[data-filter]');
    if (filterButtons.length) {
        filterButtons.forEach(button => {
            button.addEventListener('click', function() {
                filterButtons.forEach(btn => btn.classList.remove('active')); // REMOVE THE ACTIVE CLASS FROM ALL BUTTONS TO ACTIVATE ONLY THE CLICKED BUTTON
                this.classList.add('active'); // ADD THE ACTIVE CLASS TO THE CLICKED BUTTON AND APPLY THE CSS STYLES
                const filter = this.getAttribute('data-filter');
                filterPosts(filter);
            });
        });
    }
});

async function loadParentsForumPosts() {
    // TIMEOUT TO SHOW A MESSAGE IF POSTS AREN'T LOADED IN 5 SECONDS
    const timeoutId = setTimeout(() => {
        hideLoading();
        
        // SHOW THE 'NO POSTS' MESSAGE AFTER 5 SECONDS
        const container = document.getElementById('forum-posts-container');
        if (container) {
            container.innerHTML = '<div class="alert alert-info text-center p-4" role="alert">' +
                '<i class="fa-solid fa-circle-info me-2"></i>' +
                'There isn\'t any posts available yet!' +
                '</div>';
        }
    }, 5000); // 5 SECONDS TIMEOUT
    
    try {
        // CANCEL THE TIMEOUT SINCE POSTS LOADED SUCCESSFULLY
        showLoading('Loading forum posts...');
        const posts = await api.getForumPosts();
        clearTimeout(timeoutId);
        displayPosts(posts);
        hideLoading();
    } catch (error) {
        // CANCEL THE TIMEOUT SINCE WE HAVE A SPECIFIC ERROR
        clearTimeout(timeoutId);
        hideLoading();
        showError('Failed to load forum posts. Please try again later.');
        console.error('Error loading forum posts:', error);
    }
}

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
            // ADD THE NEW POST TO THE TOP OF THE LIST
            const postElement = createPostElement(newPost);
            postsContainer.insertBefore(postElement, postsContainer.firstChild);
        } else {
            // RELAOD THE POSTS IF THE CONTAINER DOESN'T EXIST
            loadParentsForumPosts();
        }
        
        hideLoading();
        showSuccess('Post created successfully');
    } catch (error) {
        hideLoading();
        showError('Failed to create post. Please try again later.');
        console.error('Error creating post:', error);
    }
}

function displayPosts(posts) {
    const container = document.getElementById('forum-posts-container');
    if (!container) return;
    
    if (posts.length === 0) {
        container.innerHTML = '<div class="alert alert-info text-center" role="status">No discussions found. Be the first to start a discussion!</div>';
        return;
    }
    
    container.innerHTML = '';
    posts.forEach(post => {
        const postElement = createPostElement(post);
        container.appendChild(postElement);
    });
}

function createPostElement(post) {
    const article = document.createElement('article');
    article.className = 'list-group-item list-group-item-action post p-3 mb-3';
    article.setAttribute('data-post-id', post.id);
    
    // Format date
    const postDate = new Date(post.created_at);
    const formattedDate = postDate.toLocaleDateString();
    
    article.innerHTML = `
        <div class="d-flex w-100 justify-content-between align-items-center">
            <h3 class="mb-2">
                <a href="/parents_forum/view/${post.id}" class="post-title">
                    ${escapeHtml(post.title)}
                </a>
            </h3>
            <small class="text-muted">${formattedDate}</small>
        </div>
        <div class="post-preview mb-3">
            <p>${escapeHtml(post.content.substring(0, 150))}${post.content.length > 150 ? '...' : ''}</p>
        </div>
        <div class="d-flex justify-content-between align-items-center">
            <div class="post-meta">
                <small class="text-muted">
                    Posted by <span class="fw-bold">${escapeHtml(post.author_username || 'Anonymous')}</span>
                </small>
            </div>
            <div class="post-stats d-flex align-items-center">
                <span class="me-3" title="Comments">
                    <i class="fa-solid fa-comments" aria-hidden="true"></i>
                    <span class="ms-1">${post.comments_count || 0}</span>
                    <span class="visually-hidden">comments</span>
                </span>
            </div>
        </div>
    `;
    
    return article;
}

function filterPosts(category) {
    const posts = document.querySelectorAll('.list-group-item');
    
    if (category === 'all') {
        posts.forEach(post => {
            post.style.display = 'block';
        });
        return;
    }
    
    // This is a placeholder - in a real application, you would have category metadata on posts
    // For demonstration, we'll hide random posts to simulate filtering
    posts.forEach(post => {
        // This is just a placeholder logic - replace with actual category filtering
        const shouldShow = Math.random() > 0.5;
        post.style.display = shouldShow ? 'block' : 'none';
    });
}

function showLoading(message = 'Loading...') {
    let loadingEl = document.getElementById('loading-indicator');
    
    if (!loadingEl) {
        loadingEl = document.createElement('div');
        loadingEl.id = 'loading-indicator';
        loadingEl.className = 'text-center my-4';
        loadingEl.innerHTML = `
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
            <p class="mt-2" id="loading-message"></p>
        `;
        
        const container = document.querySelector('.container') || document.body;
        container.prepend(loadingEl);
    }
    
    document.getElementById('loading-message').textContent = message;
}

function hideLoading() {
    const loadingEl = document.getElementById('loading-indicator');
    if (loadingEl) {
        loadingEl.remove();
    }
}

function showSuccess(message) {
    showMessage(message, 'success');
}

function showError(message) {
    showMessage(message, 'danger');
}

function showMessage(message, type) {
    const messagesContainer = document.querySelector('.messages');
    
    if (!messagesContainer) {
        // Create messages container if it doesn't exist
        const container = document.querySelector('.container') || document.body;
        const newMessagesContainer = document.createElement('div');
        newMessagesContainer.className = 'messages mb-3';
        newMessagesContainer.setAttribute('role', 'alert');
        newMessagesContainer.setAttribute('aria-live', 'polite');
        
        // Insert after headings (assuming first two rows are headings)
        const rows = container.querySelectorAll('.row');
        if (rows.length >= 2) {
            rows[1].after(newMessagesContainer);
        } else {
            container.prepend(newMessagesContainer);
        }
        
        showMessage(message, type); // Call again now that container exists
        return;
    }
    
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${escapeHtml(message)}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    messagesContainer.appendChild(alertDiv);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.classList.remove('show');
            setTimeout(() => {
                if (alertDiv.parentNode) {
                    alertDiv.parentNode.removeChild(alertDiv);
                }
            }, 150);
        }
    }, 5000);
}

// HELPER TO PREVENT XSS ATTACKS
function escapeHtml(unsafe) {
    return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}