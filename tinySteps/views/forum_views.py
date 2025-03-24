from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils.translation import gettext as _

from ..forms import ForumPost_Form
from ..models import ParentsForum_Model, Comment_Model
from ..services.forum_service import Forum_Service

def parents_forum_page(request):
    """Parents forum main page using service layer for DIP"""
    forum_service = Forum_Service()
    
    try:
        search_query = request.GET.get('search', '')
        category = request.GET.get('category', '')
        page = int(request.GET.get('page', 1))
        posts, paginator = forum_service.get_filtered_posts(search_query, category, page)
        categories = forum_service.get_categories()
        context = {
            'posts': posts,
            'paginator': paginator,
            'search_query': search_query,
            'category': category,
            'categories': categories
        }
        
        return render(request, 'forum/index.html', context)
    except Exception as e:
        from .error_views import database_error_view
        return database_error_view(request, _("Error loading forum. Please try again later."))

def search_posts(request):
    """Redirects to parents_forum_page with search parameters"""
    search_query = request.GET.get('search', '')
    category = request.GET.get('category', '')
    
    redirect_url = reverse_lazy('parents_forum')
    if search_query or category:
        redirect_url += f"?{'search=' + search_query if search_query else ''}"
        redirect_url += f"{'&' if search_query and category else ''}{'category=' + category if category else ''}"
    
    return redirect(redirect_url)

def view_post(request, post_id):
    """View a forum post using service layer for DIP"""
    forum_service = Forum_Service()
    
    try:
        post = forum_service.get_post_with_comments(post_id)
        context = {
            'post': post,
            'comments': post.comments.all().order_by('-created_at')
        }
        
        return render(request, 'forum/post_detail.html', context)
    except Exception as e:
        from .error_views import database_error_view
        return database_error_view(request, _("Error loading post. Please try again later."))

@login_required
def add_post(request):
    """Add a forum post using service layer for DIP"""
    forum_service = Forum_Service()
    
    if request.method == 'POST':
        form = ForumPost_Form(request.POST)
        if form.is_valid():
            post = forum_service.create_post(form, request.user)
            messages.success(request, _("Your post has been added successfully!"))
            return redirect('view_post', post_id=post.id)
    else:
        form = ForumPost_Form()
    
    return render(request, 'forum/add_post.html', {'form': form})

@login_required
def edit_post(request, post_id):
    """Edit a forum post using service layer for DIP"""
    forum_service = Forum_Service()
    post = forum_service.get_post(post_id)
    
    # Check if user is the author
    if post.author != request.user:
        messages.error(request, _("You can only edit your own posts."))
        return redirect('view_post', post_id=post_id)
    
    if request.method == 'POST':
        form = ForumPost_Form(request.POST, instance=post)
        if form.is_valid():
            forum_service.update_post(form, post)
            messages.success(request, _("Your post has been updated successfully!"))
            return redirect('view_post', post_id=post_id)
    else:
        form = ForumPost_Form(instance=post)
    
    return render(request, 'forum/edit_post.html', {'form': form, 'post': post})

@login_required
def delete_post(request, post_id):
    """Delete a forum post using service layer for DIP"""
    forum_service = Forum_Service()
    post = forum_service.get_post(post_id)
    
    # Check if user is the author
    if post.author != request.user:
        messages.error(request, _("You can only delete your own posts."))
        return redirect('view_post', post_id=post_id)
    
    if request.method == 'POST':
        forum_service.delete_post(post)
        messages.success(request, _("Your post has been deleted successfully!"))
        return redirect('parents_forum')
    
    return render(request, 'forum/delete_post.html', {'post': post})

@login_required
def add_post_comment(request, post_id):
    """Add a comment to a forum post using service layer for DIP"""
    forum_service = Forum_Service()
    
    if request.method == 'POST':
        text = request.POST.get('text')
        if text:
            forum_service.add_comment(post_id, request.user, text)
            messages.success(request, _("Your comment has been added successfully!"))
        else:
            messages.error(request, _("Comment cannot be empty."))
    
    return redirect('view_post', post_id=post_id)

@login_required
def forum_post_like_toggle(request, post_id, forum_service=None):
    service = forum_service or Forum_Service()
    is_liked = service.toggle_like(post_id, request.user)
    
    if is_liked:
        messages.success(request, _("Post added to favorites!"))
    else:
        messages.info(request, _("Post removed from favorites."))
    
    return redirect('view_post', post_id=post_id)