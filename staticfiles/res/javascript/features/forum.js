import api from "../core/api.js";
import { escapeHtml } from "../core/utils.js";
import {
  showLoading,
  hideLoading,
  showSuccess,
  showError,
} from "../core/ui.js";

// Load forum posts
async function loadForumPosts() {
  const timeoutId = setTimeout(() => {
    hideLoading();

    // If loading takes too long, show a message to the user
    const container = document.getElementById("forum-posts-container");
    if (container) {
      container.innerHTML =
        '<div class="alert alert-info text-center p-4" role="alert">' +
        '<i class="fa-solid fa-circle-info me-2"></i>' +
        "There isn't any posts available yet!" +
        "</div>";
    }
  }, 5000); // 5 seconds timeout

  try {
    showLoading("Loading forum posts...");
    const posts = await api.getForumPosts();
    clearTimeout(timeoutId);
    displayPosts(posts);
    hideLoading();
  } catch (error) {
    clearTimeout(timeoutId);
    hideLoading();
    showError("Failed to load forum posts. Please try again later.");
    console.error("Error loading forum posts:", error);
  }
}

// Display posts in the forum
function displayPosts(posts) {
  const container = document.getElementById("forum-posts-container");
  if (!container) return;

  if (posts.length === 0) {
    container.innerHTML =
      '<div class="alert alert-info text-center" role="status">No discussions found. Be the first to start a discussion!</div>';
    return;
  }

  container.innerHTML = "";
  posts.forEach((post) => {
    const postElement = createPostElement(post);
    container.appendChild(postElement);
  });
}

// Create post element for forum list
function createPostElement(post) {
  const article = document.createElement("article");
  article.className = "list-group-item list-group-item-action post p-3 mb-3";
  article.setAttribute("data-post-id", post.id);

  // Format date
  const postDate = new Date(post.created_at);
  const formattedDate = postDate.toLocaleDateString();

  article.innerHTML = `
        <div class="d-flex w-100 justify-content-between align-items-center">
            <h3 class="mb-2">
                <a href="/parent_forum/view/${post.id}" class="post-title">
                    ${escapeHtml(post.title)}
                </a>
            </h3>
            <small class="text-muted">${formattedDate}</small>
        </div>
        <div class="post-preview mb-3">
            <p>${escapeHtml(post.content.substring(0, 150))}${
    post.content.length > 150 ? "..." : ""
  }</p>
        </div>
        <div class="d-flex justify-content-between align-items-center">
            <div class="post-meta">
                <small class="text-muted">
                    Posted by <span class="fw-bold">${escapeHtml(
                      post.author_username || "Anonymous"
                    )}</span>
                </small>
            </div>
            <div class="post-stats d-flex align-items-center">
                <span class="me-3" title="Comments">
                    <i class="fa-solid fa-comments" aria-hidden="true"></i>
                    <span class="ms-1">${post.comments_count || 0}</span>
                    <span class="visually-hidden">comments</span>
                </span>
                <span title="Likes">
                    <i class="fa-solid fa-heart" aria-hidden="true"></i>
                    <span class="ms-1">${post.likes_count || 0}</span>
                    <span class="visually-hidden">likes</span>
                </span>
            </div>
        </div>
    `;

  return article;
}

// Create new post
async function createPost(data) {
  try {
    showLoading("Creating post...");
    const newPost = await api.createForumPost(data);
    hideLoading();
    showSuccess("Post created successfully");
    return newPost;
  } catch (error) {
    hideLoading();
    showError("Failed to create post. Please try again later.");
    console.error("Error creating post:", error);
    throw error;
  }
}

// Filter posts by category
function filterPosts(category) {
  const posts = document.querySelectorAll(".list-group-item");

  if (category === "all") {
    posts.forEach((post) => {
      post.style.display = "block";
    });
    return;
  }

  posts.forEach((post) => {
    const shouldShow = Math.random() > 0.5;
    post.style.display = shouldShow ? "block" : "none";
  });
}

export {
  loadForumPosts,
  displayPosts,
  createPostElement,
  createPost,
  filterPosts,
};
