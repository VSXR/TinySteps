import api from "../core/api.js";
import { escapeHtml, isAuthenticated } from "../core/utils.js";
import {
    showLoading,
    hideLoading,
    showSuccess,
    showError,
    showLoginPrompt,
} from "../core/ui.js";
import {
    loadComments,
    displayComments,
    setupCommentForm,
} from "../features/comments.js";
import {
    likePost,
    sharePost,
    setupLikeButtons,
} from "../features/interactions.js";

function getPostIdFromUrl() {
    return window.location.pathname.split("/").filter(Boolean).pop();
}

function handleLoadingTimeout() {
    // Update content area with message
    const contentElement = document.querySelector(".post-content");
    if (contentElement) {
        contentElement.innerHTML =
            '<div class="alert alert-info text-center p-4" role="alert">' +
            '<i class="fa-solid fa-circle-info me-2"></i>' +
            "There isn't any post available yet!" +
            "</div>";
    }

    // Reset counts
    const likeCountElement = document.getElementById("like-count");
    if (likeCountElement) {
        likeCountElement.textContent = "0";
    }

    const commentCountElement = document.querySelector("h2#comments-heading");
    if (commentCountElement) {
        commentCountElement.textContent = "Comments (0)";
    }

    // Update comments area
    const commentListElement = document.querySelector(".comment-list");
    if (commentListElement) {
        const noCommentsElement = document.createElement("p");
        noCommentsElement.className = "text-center my-4";
        noCommentsElement.textContent = "No comments available.";
        commentListElement.parentNode.replaceChild(
            noCommentsElement,
            commentListElement
        );
    }
}

// UI Update Functions
function updateLikeButtonState(response) {
    if (!response) return;

    const likeButton = document.getElementById("like-button");
    const likeCount = document.getElementById("like-count");

    if (likeCount && response.likes_count !== undefined) {
        likeCount.textContent = response.likes_count;
    }

    if (likeButton && response.liked !== undefined) {
        if (response.liked) {
            likeButton.classList.add("liked", "btn-primary");
            likeButton.classList.remove("btn-outline-primary");
            likeButton.setAttribute("aria-pressed", "true");
            showSuccess("Post liked!");
        } else {
            likeButton.classList.remove("liked", "btn-primary");
            likeButton.classList.add("btn-outline-primary");
            likeButton.setAttribute("aria-pressed", "false");
            showSuccess("Post unliked");
        }
    }
}

function updatePostTags(tags) {
    const tagsContainer = document.querySelector(".post-tags");
    if (!tagsContainer) return;

    tagsContainer.innerHTML =
        '<h2 id="post-categories" class="visually-hidden">Post Categories</h2>';

    tags.forEach((tag) => {
        const tagLink = document.createElement("a");
        tagLink.href = `/parent_forum/?tag=${encodeURIComponent(tag.slug)}`;
        tagLink.className = "badge bg-primary text-decoration-none me-1 mb-1";
        tagLink.textContent = `#${tag.name}`;
        tagsContainer.appendChild(tagLink);
    });
}

function updatePostDetails(post) {
    // Update post title
    const titleElement = document.querySelector("h1.fs-4");
    if (titleElement) titleElement.textContent = post.title;

    // Update post content
    const contentElement = document.querySelector(".post-content");
    if (contentElement) {
        contentElement.innerHTML = post.content || post.desc;
    }

    // Update author and date
    const authorElement = document.querySelector(".post-author");
    if (authorElement) {
        authorElement.innerHTML = `<span class="fw-bold">Posted by:</span> ${escapeHtml(
            post.author.username
        )}`;
    }

    // Update date
    const dateElement = document.querySelector(".post-date time");
    if (dateElement) {
        const postDate = new Date(post.created_at);
        dateElement.setAttribute("datetime", postDate.toISOString().split("T")[0]);
        dateElement.textContent = postDate.toLocaleDateString("en-US", {
            year: "numeric",
            month: "long",
            day: "numeric",
        });
    }

    // Update like count
    const likeCountElement = document.getElementById("like-count");
    if (likeCountElement) {
        likeCountElement.textContent = post.likes_count || 0;
    }

    // Update comment count
    const commentCountElement = document.querySelector("h2#comments-heading");
    if (commentCountElement) {
        commentCountElement.textContent = `Comments (${post.comments_count || 0})`;
    }

    // Update like button state
    if (
        post.tags &&
        post.tags.length > 0 &&
        document.querySelector(".post-tags")
    ) {
        updatePostTags(post.tags);
    }

    document.title = `${post.title} - TinySteps Forum`;
}

// Core Functionality
async function handleLikePost(postId) {
    if (!isAuthenticated()) {
        showLoginPrompt("Please log in to like this post");
        return;
    }

    try {
        showLoading("Processing...");
        const response = await likePost(postId);
        hideLoading();
        updateLikeButtonState(response);
    } catch (error) {
        hideLoading();
        showError("Failed to process your like. Please try again.");
        console.error("Error liking post:", error);
    }
}

async function loadPostDetails(postId) {
    const timeoutId = setTimeout(() => {
        hideLoading();
        handleLoadingTimeout();
    }, 3000); // 3 seconds

    try {
        showLoading("Loading post details...");

        // Load post details and comments
        const post = await api.getForumPost(postId);
        clearTimeout(timeoutId);

        updatePostDetails(post);
        await loadComments(postId);

        hideLoading();
    } catch (error) {
        clearTimeout(timeoutId);
        hideLoading();
        showError("Failed to load post. Please try again later.");
        console.error("Error loading post:", error);
    }
}

// Comment deletion functionality
function setupCommentDeletion() {
    // Get all delete comment buttons
    const deleteButtons = document.querySelectorAll('.btn-delete-comment');
    
    deleteButtons.forEach(button => {
        button.addEventListener('click', function() {
            if (confirm('Are you sure you want to delete this comment? This action cannot be undone.')) {
                const commentId = this.getAttribute('data-comment-id');
                deleteComment(commentId);
            }
        });
    });
}

function deleteComment(commentId) {
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    
    fetch(`/forum/comments/${commentId}/delete/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken,
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        credentials: 'same-origin'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Remove the comment from the DOM
            const commentElement = document.getElementById(`comment-${commentId}`);
            if (commentElement) {
                commentElement.remove();
                
                // Update comment count
                const commentCount = document.querySelectorAll('.comment-list .card').length;
                const commentsHeading = document.querySelector('#comments-heading');
                if (commentsHeading) {
                    commentsHeading.textContent = `Comments (${commentCount})`;
                }
                
                // Show success message
                showSuccess('Comment deleted successfully');
                
                // If no comments left, show the "no comments" message
                if (commentCount === 0) {
                    const commentList = document.querySelector('.comment-list');
                    if (commentList) {
                        const noCommentsElement = document.createElement('div');
                        noCommentsElement.className = 'card border-0 shadow-sm rounded-4 mb-4 text-center py-4';
                        noCommentsElement.innerHTML = `
                            <i class="fa-regular fa-comment fa-2x text-muted mb-2" aria-hidden="true"></i>
                            <p>No comments yet. Be the first to comment!</p>
                        `;
                        commentList.parentNode.replaceChild(noCommentsElement, commentList);
                    }
                }
            }
        } else {
            // Show error message
            showError(data.error || 'Failed to delete comment');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showError('An error occurred while deleting the comment');
    });
}

function setupEventHandlers(postId) {
    const likeButton = document.getElementById("like-button");
    if (likeButton) {
        likeButton.addEventListener("click", () => handleLikePost(postId));
    }

    setupCommentForm();
    setupCommentDeletion();
    
    const shareButton = document.querySelector("[data-share-post]");
    if (shareButton) {
        shareButton.addEventListener("click", () => sharePost(postId));
    }
}

function initPostPage() {
    const postId = getPostIdFromUrl();

    if (postId) {
        loadPostDetails(postId);
        setupEventHandlers(postId);
    }
}

document.addEventListener("DOMContentLoaded", initPostPage);
export { initPostPage };
