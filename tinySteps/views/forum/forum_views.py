from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.translation import gettext as _

from tinySteps.forms import ForumPost_Form, ForumComment_Form
from tinySteps.services import Forum_Service
from tinySteps.models import ParentsForum_Model

def parents_forum_page(request):
    """Main forum page"""
    service = Forum_Service()
    posts = service.get_posts()
    
    context = {
        'posts': posts,
    }
    
    return render(request, 'forum/index.html', context)

def search_posts(request):
    """Search forum posts"""
    service = Forum_Service()
    query = request.GET.get('q', '')
    category = request.GET.get('category', '')
    
    posts = service.search_posts(query, category)
    
    context = {
        'posts': posts,
        'query': query,
        'category': category,
        'categories': service.get_categories()
    }
    
    return render(request, 'forum/search_results.html', context)

def view_post(request, post_id):
    """View a specific forum post"""
    service = Forum_Service()
    post = service.get_post(post_id)
    
    # We handle comment submission
    if request.method == 'POST' and request.user.is_authenticated:
        content = request.POST.get('content', '').strip()
        if content:
            service.add_comment(post_id, request.user, content)
            messages.success(request, _("Your comment has been added."))
            return redirect('view_post', post_id=post_id)
    
    comments = service.get_post_comments(post_id)
    form = ForumComment_Form()
    
    context = {
        'post': post,
        'comments': comments,
        'form': form,
    }
    
    return render(request, 'forum/posts/detail.html', context)

@login_required
def add_post(request):
    """Add a new forum post"""
    if request.method == 'POST':
        form = ForumPost_Form(request.POST)
        if form.is_valid():
            service = Forum_Service()
            post = service.create_post(request.user, 
                                      form.cleaned_data['title'], 
                                      form.cleaned_data['desc'], 
                                      form.cleaned_data['category'])
            messages.success(request, _("Your post has been published."))
            return redirect('view_post', post_id=post.id)
    else:
        form = ForumPost_Form()
    
    context = {
        'form': form,
        'post_category_choices': ParentsForum_Model.CATEGORY_CHOICES
    }
    
    return render(request, 'forum/posts/create.html', context)

@login_required
def edit_post(request, post_id):
    """Edit an existing forum post"""
    service = Forum_Service()
    post = service.get_post(post_id)
    
    # Check if user is the author
    if post.author != request.user:
        messages.error(request, _("You don't have permission to edit this post."))
        return redirect('view_post', post_id=post_id)
    
    if request.method == 'POST':
        form = ForumPost_Form(request.POST, instance=post)
        if form.is_valid():
            service.update_post(post_id, form.cleaned_data['title'], 
                              form.cleaned_data['desc'], 
                              form.cleaned_data['category'])
            messages.success(request, _("Your post has been updated."))
            return redirect('view_post', post_id=post_id)
    else:
        form = ForumPost_Form(instance=post)
    
    context = {
        'form': form,
        'post': post,
        'post_category_choices': ParentsForum_Model.CATEGORY_CHOICES
    }
    
    return render(request, 'forum/posts/edit.html', context)

@login_required
def delete_post(request, post_id):
    """Delete a forum post"""
    service = Forum_Service()
    post = service.get_post(post_id)
    
    if not (post.author == request.user or request.user.is_staff or request.user.is_superuser):
        messages.error(request, _("You don't have permission to delete this post."))
        return redirect('view_post', post_id=post_id)
    
    if request.method == 'POST':
        service.delete_post(post_id)
        messages.success(request, _("Your post has been deleted."))
        return redirect('parent_forum')
    
    return render(request, 'forum/posts/delete.html', {'post': post})

@login_required
def add_post_comment(request, post_id):
    """Add a comment to a forum post"""
    if request.method == 'POST':
        form = ForumComment_Form(request.POST)
        if form.is_valid():
            service = Forum_Service()
            service.add_comment(post_id, form.cleaned_data, request.user)
            messages.success(request, _("Your comment has been added."))
    
    return redirect('view_post', post_id=post_id)

@login_required
def forum_post_like_toggle(request, post_id):
    """Toggle like status for a forum post"""
    service = Forum_Service()
    service.toggle_like(post_id, request.user)
    
    # Return to the previous page after toggling like (goes to forum home if no referer!)
    return redirect(request.META.get('HTTP_REFERER', 'parent_forum'))