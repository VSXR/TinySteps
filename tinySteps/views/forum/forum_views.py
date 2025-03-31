from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.utils.translation import gettext as _

from tinySteps.forms import ForumPost_Form, ForumComment_Form
from tinySteps.models import ParentsForum_Model
from tinySteps.services import Forum_Service

def parents_forum_page(request):
    """Main forum page"""
    service = Forum_Service()
    category = request.GET.get('category', '')
    query = request.GET.get('q', '')
    
    if category or query:
        posts_list = service.search_posts(query, category)
    else:
        posts_list = service.get_posts()
    
    # Pagination
    page = request.GET.get('page', 1)
    paginator = Paginator(posts_list, 4)  # We show 4 posts per page
    
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    
    context = {
        'posts': posts,
        'forum_categories': service.get_categories(),
        'category_counts': service.get_category_counts(),
        'view_type': 'list'
    }
    
    return render(request, 'forum/index.html', context)

def search_posts(request):
    """Search forum posts"""
    service = Forum_Service()
    query = request.GET.get('q', '')
    category = request.GET.get('category', '')
    
    posts_list = service.search_posts(query, category)
    page = request.GET.get('page', 1)
    paginator = Paginator(posts_list, 10)  # we show 10 posts per page
    
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    
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
            return redirect('forum:view_post', post_id=post_id)
    
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
            return redirect('forum:view_post', post_id=post.id)
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
        return redirect('forum:view_post', post_id=post_id)
    
    if request.method == 'POST':
        form = ForumPost_Form(request.POST, instance=post)
        if form.is_valid():
            service.update_post(post_id, form.cleaned_data['title'], 
                              form.cleaned_data['desc'], 
                              form.cleaned_data['category'])
            messages.success(request, _("Your post has been updated."))
            return redirect('forum:view_post', post_id=post_id)
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
        return redirect('forum:view_post', post_id=post_id)
    
    if request.method == 'POST':
        service.delete_post(post_id)
        messages.success(request, _("Your post has been deleted."))
        return redirect('forum:parent_forum')
    
    return render(request, 'forum/posts/delete.html', {'post': post})

@login_required
def add_post_comment(request, post_id):
    """Add a comment to a forum post"""
    if request.method == 'POST':
        content = request.POST.get('content', '')
        
        if not content.strip():
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': 'Comment text is required'})
            messages.error(request, _("Comment text is required"))
            return redirect('forum:view_post', post_id=post_id)
            
        try:
            service = Forum_Service()
            comment = service.add_comment(
                post_id,
                request.user,
                content
            )
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True})
            
            messages.success(request, _("Comment added successfully"))
            return redirect('forum:view_post', post_id=post_id)
                
        except ValueError as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': str(e)})
            messages.error(request, str(e))
            return redirect('forum:view_post', post_id=post_id)
    
    return redirect('forum:view_post', post_id=post_id)

@login_required
def forum_post_like_toggle(request, post_id):
    pass

@login_required
def categories(request):
    pass