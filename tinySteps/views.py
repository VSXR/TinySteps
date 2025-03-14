import logging
from django import forms
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, views as auth_views
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db import models
from django.db.models import Q, Prefetch
from django.utils import timezone
from django.http import Http404, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.views import generic
from django.views.generic.edit import CreateView

# LOCAL IMPORTS
from .forms import (
    InfoRequest_Form, 
    Milestone_Form,
    PasswordReset_Form,
    CustomUserCreation_Form,
    YourChild_Form,
)
from .models import (
    InfoRequest_Model, 
    YourChild_Model, 
    ParentsForum_Model,
    Guides_Model, # BASE MODEL FOR PARENTS AND NUTRITION GUIDES
    ParentsGuides_Model,
    NutritionGuides_Model,
    Comment_Model,
    Like_Model,
)

# -----------------------------------------------
# -- GENERAL FUNCTION-BASED VIEWS --
# -----------------------------------------------
def index(request):
    return render(request, 'pages/index.html')

def about(request):
    return render(request, 'pages/about.html')

def page_not_found(request, exception):
    return render(request, 'pages/404.html', status=404)

# -----------------------------------------------


# -----------------------------------------------
# -- LOGIN, LOGOUT AND REGISTER CLASS-VIEWS --
# -----------------------------------------------
class Login_View(auth_views.LoginView):
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        return reverse_lazy('index')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Login successful!")
        return response
    
    def form_invalid(self, form):
        messages.error(self.request, "Usuario o contraseña incorrectos. ¿No tienes cuenta? Regístrate ahora.")
        return super().form_invalid(form)
    
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('index')
        return super().get(request, *args, **kwargs)

class Logout_View(auth_views.LogoutView):
    next_page = 'index'
    
    def dispatch(self, request, *args, **kwargs):
            messages.success(request, 'You have been successfully logged out!')
            return super().dispatch(request, *args, **kwargs)

class Register_View(CreateView):
    form_class = CustomUserCreation_Form
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('index')
    
    def get_success_url(self):
        return reverse_lazy('index')
    
    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        messages.success(self.request, "Registration successful!")
        return super().form_valid(form)
    
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('index')
        return super().get(request, *args, **kwargs)
@login_required
def profile(request):
    # We get the children of the user and the forum posts they have created
    children = YourChild_Model.objects.filter(user=request.user)
    
    forum_posts = ParentsForum_Model.objects.filter(author=request.user)\
        .annotate(comments_count=models.Count('comments'))\
        .order_by('-created_at')
    
    context = {
        'children': children,
        'forum_posts': forum_posts[:5],
    }
    
    return render(request, 'accounts/profile.html', context)
# -----------------------------------------------

# ------------------------------------------
# -- PASSWORD RESET VIEWS --
# ------------------------------------------
def password_reset(request):
    if request.method == 'POST':
        form = PasswordReset_Form(request.POST)
        if form.is_valid():
            # Si el formulario es válido, obtenemos el usuario
            username = form.cleaned_data['username']
            user = User.objects.get(username=username)
            
            # Establecemos la nueva contraseña
            password = form.cleaned_data['new_password1']
            user.set_password(password)
            user.save()
            
            messages.success(request, "Your password has been updated successfully! You can now log in.")
            return redirect('login')
    else:
        form = PasswordReset_Form()
    
    return render(request, 'accounts/user_password/reset_password.html', {'form': form})

# ------------------------------------------


# -----------------------------------------------
# -- YOUR_CHILDREN FUNCTION-BASED VIEWS --
# -----------------------------------------------
@login_required(login_url='login')
def your_children(request):
    children = YourChild_Model.objects.filter(user=request.user)
    return render(request, 'children/list.html', {'children': children})

@login_required(login_url='login')
def your_child(request, pk):
    child = get_object_or_404(YourChild_Model, pk=pk)
    return render(request, 'children/detail.html', {'child': child})

@login_required
def child_milestone(request, child_id):
    child = get_object_or_404(YourChild_Model, id=child_id, user=request.user)
    
    if request.method == 'POST':
        form = Milestone_Form(request.POST, request.FILES)
        if form.is_valid():
            milestone = form.save(commit=False)
            milestone.child = child
            milestone.save()
            messages.success(request, "Milestone added!")
            return redirect('your_child', pk=child_id)
    else:
        form = Milestone_Form()
    
    return render(request, 'children/features/milestones/index.html', {
        'form': form, 
        'child': child,
        'today': timezone.now().date()
    })

# -----------------------------------------------

# -----------------------------------------------
# -- YOUR CHILDREN CLASS-VIEWS --
# -----------------------------------------------
class YourChild_Add_View(LoginRequiredMixin, SuccessMessageMixin, generic.CreateView):
    login_url = 'login'
    template_name = 'children/actions/create.html'
    model = YourChild_Model
    form_class = YourChild_Form
    success_url = reverse_lazy('your_children')
    success_message = "Child added successfully!"

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)
    
    def post(self, request, *args, **kwargs):
        form = self.get_form()
        form.instance.user = request.user
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

class YourChild_Delete_View(LoginRequiredMixin, SuccessMessageMixin, generic.DeleteView):
    login_url = 'login'
    template_name = 'children/actions/delete.html'
    model = YourChild_Model
    success_url = reverse_lazy('your_children')
    success_message = "Child removed successfully!"
    
    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        messages.success(self.request, self.success_message)
        return response
    
    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)
    
    def get_object(self, queryset=None):
        obj = super().get_object()
        if not obj.user == self.request.user:
            raise Http404
        return obj
    
    def get_success_url(self):
        return reverse_lazy('your_children')

class YourChild_UpdateDetails_View(LoginRequiredMixin, SuccessMessageMixin, generic.UpdateView):
    login_url = 'login'
    template_name = 'children/actions/edit.html'
    model = YourChild_Model
    form_class = YourChild_Form
    success_message = "Child information updated successfully!"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['children'] = YourChild_Model.objects.filter(user=self.request.user)
        return context
    
    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)
    
    def get_object(self, queryset=None):
        obj = super().get_object()
        if not obj.user == self.request.user:
            raise Http404
        return obj
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        self.object = form.save(commit=True)  
        self.object.refresh_from_db() # Importante: Forzamos el guardado y la recarga del objeto para evitar problemas con las relaciones!
        
        messages.success(self.request, "Child information updated successfully!")
        return super().form_valid(form)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.form_class(request.POST, request.FILES, instance=self.object)
        if form.is_valid():
            return self.form_valid(form)
        return self.form_invalid(form)

    def get_success_url(self):
        return reverse_lazy('child_details', kwargs={'pk': self.object.pk})


# -----------------------------------------------
# --- CHILD FEATURES CLASS-VIEWS ---
# -----------------------------------------------
class YourChild_Calendar_View(LoginRequiredMixin, generic.DetailView):
    login_url = 'login'
    template_name = 'children/features/calendar/index.html'
    model = YourChild_Model
    
    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)
    
    def get_object(self, queryset=None):
        obj = super().get_object()
        if not obj.user == self.request.user:
            raise Http404
        return obj
    
class YourChild_VaccineCard_View(LoginRequiredMixin, generic.DetailView):
    login_url = 'login'
    template_name = 'children/features/vaccine-card/index.html'
    model = YourChild_Model
    
    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)
    
    def get_object(self, queryset=None):
        obj = super().get_object()
        if not obj.user == self.request.user:
            raise Http404
        return obj

# -----------------------------------------------

# -----------------------------------------------
# -- COMMENTS FUNCTION-BASED VIEWS --
# -----------------------------------------------
def add_comment(request, model_type, pk):
    if model_type == 'forum':
        obj = get_object_or_404(ParentsForum_Model, pk=pk)
    elif model_type == 'parent_guide':
        obj = get_object_or_404(ParentsGuides_Model, pk=pk)
    elif model_type == 'nutrition_guide':
        obj = get_object_or_404(NutritionGuides_Model, pk=pk)
    else:
        raise Http404("Tipo de contenido no válido")
    
    if request.method == 'POST':
        text = request.POST.get('text')
        if text:
            Comment_Model.objects.create(
                content_object=obj,
                author=request.user,
                text=text
            )
            messages.success(request, "Comentario añadido correctamente.")
        return redirect(obj.get_absolute_url())

# -----------------------------------------------

# -----------------------------------------------
# -- LIKES FUNCTION-BASED VIEWS --
# -----------------------------------------------
@login_required
def like_toggle(request, content_type_id, object_id):
    content_type = get_object_or_404(ContentType, id=content_type_id)
    
    try:
        obj = content_type.get_object_for_this_type(id=object_id)
        like_exists = Like_Model.objects.filter(
            content_type=content_type,
            object_id=object_id,
            user=request.user
        ).exists()
        
        if like_exists:
            # Unlike
            Like_Model.objects.filter(
                content_type=content_type,
                object_id=object_id,
                user=request.user
            ).delete()
            liked = False
        else:
            # Like
            Like_Model.objects.create(
                content_type=content_type,
                object_id=object_id,
                user=request.user
            )
            liked = True
        
        likes_count = Like_Model.objects.filter(
            content_type=content_type,
            object_id=object_id
        ).count()
        
        return JsonResponse({
            'status': 'success',
            'liked': liked,
            'likes_count': likes_count
        })
        
    except Exception as e:
        logging.error(f"Error in like_toggle: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': 'An error occurred processing your request'
        }, status=400)

# -----------------------------------------------

# -----------------------------------------------
# -- PARENTS FORUM FUNCTION-BASED VIEWS --
# -----------------------------------------------
def parents_forum_page(request):
    posts_list = ParentsForum_Model.objects.select_related('author').all()
    content_type = ContentType.objects.get_for_model(ParentsForum_Model)
    
    posts_list = posts_list.prefetch_related(
        Prefetch('comments', 
                 queryset=Comment_Model.objects.filter(
                     content_type=content_type
                 ).select_related('author')
        )
    )

    # Filtrar por búsqueda
    query = request.GET.get('search')
    if query:
        posts_list = posts_list.filter(title__icontains=query)
        
    # Filtrar por categoría
    category = request.GET.get('category')
    if category:
        posts_list = posts_list.filter(category=category)
    
    # Ordenar resultados
    sort = request.GET.get('sort', 'created_at')
    if sort == 'title':
        posts_list = posts_list.order_by('title')
    elif sort == 'most_liked':
        content_type = ContentType.objects.get_for_model(ParentsForum_Model)
        posts_list = posts_list.annotate(
            likes_count=models.Count(
                'like_model',
                filter=models.Q(like_model__content_type=content_type)
            )
        ).order_by('-likes_count', '-created_at')
    elif sort == 'most_commented':
        content_type = ContentType.objects.get_for_model(ParentsForum_Model)
        posts_list = posts_list.annotate(
            comments_count=models.Count(
                'comment_model',
                filter=models.Q(comment_model__content_type=content_type)
            )
        ).order_by('-comments_count', '-created_at')
    else:
        posts_list = posts_list.order_by('-created_at')
    
    # Paginación
    paginator = Paginator(posts_list, 10)
    page = request.GET.get('page')
    try:
        posts = paginator.get_page(page)
    except (PageNotAnInteger, EmptyPage):
        posts = paginator.page(1)
    
    return render(request, 'forum/index.html', {
        'posts': posts,
        'selected_sort': sort,
        'query': query,
        'category': category
    })

def search_posts(request):
    query = request.GET.get('q', '')
    if query:
        posts_list = ParentsForum_Model.objects.filter(
            Q(title__icontains=query) | 
            Q(desc__icontains=query)
        ).order_by('-created_at')
    else:
        posts_list = ParentsForum_Model.objects.all().order_by('-created_at')
    
    paginator = Paginator(posts_list, 10)
    page = request.GET.get('page', 1)
    try:
        posts = paginator.page(page)
    except (PageNotAnInteger, EmptyPage):
        posts = paginator.page(1)
    
    return render(request, 'forum/index.html', {
        'posts': posts,
        'query': query
    })

@login_required
def add_post(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('desc')
        
        if title and content:
            post = ParentsForum_Model.objects.create(
                title=title,
                desc=content,
                author=request.user
            )
            messages.success(request, "Post created successfully!")
            return redirect('view_post', post_id=post.id)
        else:
            messages.error(request, "Please fill all required fields")
    
    return render(request, 'forum/posts/create.html')

@login_required
def view_posts_list(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('desc')
        
        if title and content:
            post = ParentsForum_Model.objects.create(
                title=title,
                desc=content,
                author=request.user
            )
            messages.success(request, "Post created successfully!")
            return redirect('view_post', post_id=post.id)
        else:
            messages.error(request, "Please fill all required fields")
            return redirect('add_post')
    
    return redirect('view_post', post_id=post.id)

@login_required
def edit_post(request, post_id):
    post = get_object_or_404(ParentsForum_Model, id=post_id)
    
    if request.user == post.author or request.user.is_staff or request.user.is_superuser:
        if request.method == 'POST':
            title = request.POST.get('title')
            content = request.POST.get('desc')

            if title and content:
                post.title = title
                post.desc = content
                post.save()
                messages.success(request, "Post updated successfully!")
                return redirect('view_post', post_id=post.id)
            else:
                messages.error(request, "Please fill all required fields")
        
        return render(request, 'forum/posts/edit.html', {'post': post})
    else:
        messages.error(request, "You don't have permission to edit this post")
        return redirect('parents_forum')

@login_required
def delete_post(request, post_id):
    post = get_object_or_404(ParentsForum_Model, id=post_id)
    
    if request.user == post.author or request.user.is_staff or request.user.is_superuser:
        if request.method == 'POST':
            post.delete()
            messages.success(request, "Post deleted successfully!")
            return redirect('parents_forum')
        
        return render(request, 'forum/posts/delete.html', {'post': post})
    else:
        messages.error(request, "You don't have permission to delete this post")
        return redirect('parents_forum')

def view_post(request, post_id):
    post = get_object_or_404(ParentsForum_Model, id=post_id)
    related_posts = ParentsForum_Model.objects.filter(author=post.author).exclude(id=post_id)[:4]
    
    user_liked = False
    if request.user.is_authenticated:
        user_liked = post.likes.filter(id=request.user.id).exists()
    
    return render(request, 'forum/posts/detail.html', {
        'post': post,
        'related_posts': related_posts,
        'user_liked': user_liked
    })

@login_required
def add_post_comment(request, post_id):
    post = get_object_or_404(ParentsForum_Model, id=post_id)
    
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            Comment_Model.objects.create(
                content_object=post,
                author=request.user,
                text=content
            )
            messages.success(request, "Comment added successfully!")
        else:
            messages.error(request, "Please enter a comment.")
    
    return redirect('view_post', post_id=post.id)

@login_required
def forum_post_like_toggle(request, post_id):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)
    
    try:
        post = get_object_or_404(ParentsForum_Model, pk=post_id)
        content_type = ContentType.objects.get_for_model(ParentsForum_Model)
        
        # Check if user already liked this post
        like_exists = Like_Model.objects.filter(
            content_type=content_type,
            object_id=post_id,
            user=request.user
        ).exists()
        
        if like_exists:
            # Unlike
            Like_Model.objects.filter(
                content_type=content_type,
                object_id=post_id,
                user=request.user
            ).delete()
            liked = False
        else:
            # Like
            Like_Model.objects.create(
                content_type=content_type,
                object_id=post_id,
                user=request.user
            )
            liked = True
        
        # Get total likes count
        likes_count = Like_Model.objects.filter(
            content_type=content_type,
            object_id=post_id
        ).count()
        
        return JsonResponse({
            'status': 'success',
            'liked': liked,
            'likes_count': likes_count
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': 'An error occurred processing your request'
        }, status=400)


# -----------------------------------------------
# -- PARENTS FORUM CLASS-VIEWS --
# -----------------------------------------------
class ParentsForum_Add_View(LoginRequiredMixin, SuccessMessageMixin, generic.CreateView):
    login_url = 'login'
    template_name = 'forum/posts/create.html'
    model = ParentsForum_Model
    fields = ['title', 'desc']
    success_url = reverse_lazy('parents_forum')
    success_message = "Forum created successfully!"
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)
    
    def get_queryset(self):
        return super().get_queryset().filter(author=self.request.user)
    
    def get_success_url(self):
        return reverse_lazy('parents_forum')
    
class ParentsForum_Update_View(LoginRequiredMixin, SuccessMessageMixin, generic.UpdateView):
    login_url = 'login'
    template_name = 'forum/posts/edit.html'
    model = ParentsForum_Model
    fields = ['title', 'desc']
    success_url = reverse_lazy('parents_forum')
    success_message = "Forum updated successfully!"

    def get_queryset(self):
        return super().get_queryset().filter(author=self.request.user)
    
    def get_object(self, queryset=None):
        obj = super().get_object()
        if not obj.author == self.request.user:
            raise Http404
        return obj
    
    def get_success_url(self):
        return reverse_lazy('parents_forum')

class ParentsForum_Delete_View(LoginRequiredMixin, SuccessMessageMixin, generic.DeleteView):
    login_url = 'login'
    template_name = 'forum/posts/delete.html'
    model = ParentsForum_Model
    success_url = reverse_lazy('parents_forum')
    success_message = "Forum deleted successfully!"
    
    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        messages.success(self.request, self.success_message)
        return response
    
    def get_queryset(self):
        # Permitir a administradores ver todos los posts
        if self.request.user.is_staff or self.request.user.is_superuser:
            return ParentsForum_Model.objects.all()
        # Usuarios normales solo ven sus propios posts
        return super().get_queryset().filter(author=self.request.user)
    
    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        # Permitir a administradores acceder a cualquier post
        if self.request.user.is_staff or self.request.user.is_superuser:
            return obj
        # Para usuarios normales, verificar si son autores
        if not obj.author == self.request.user:
            raise Http404
        return obj
    
    def get_success_url(self):
        return reverse_lazy('parents_forum')

# -----------------------------------------------


# -----------------------------------------------
# -- GUIDES FUNCTION-BASED VIEWS --
# -----------------------------------------------
def guides_page(request):
    """Main landing page for guides, showing both nutrition and parent guides"""
    parent_guides = Guides_Model.objects.filter(guide_type='parent')[:4]
    nutrition_guides = Guides_Model.objects.filter(guide_type='nutrition')[:4]
    return render(request, 'guides/index.html', {
        'parent_guides': parent_guides,
        'nutrition_guides': nutrition_guides
    })

def parents_guides_page(request):
    parents_guides = Guides_Model.objects.filter(guide_type='parent')
    return render(request, 'guides/parents/list.html', {'parents_guides': parents_guides})

def parent_guide_details(request, pk):
    guide = get_object_or_404(Guides_Model, pk=pk, guide_type='parent')
    return render(request, 'guides/parents/detail.html', {'parent_guide': guide})

def nutrition_guides_page(request):
    nutrition_guides = Guides_Model.objects.filter(guide_type='nutrition')
    return render(request, 'guides/nutrition/list.html', {'nutrition_guides': nutrition_guides})

def nutrition_guide_details(request, pk):
    guide = get_object_or_404(Guides_Model, pk=pk, guide_type='nutrition')
    return render(request, 'guides/nutrition/detail.html', {'nutrition_guide': guide})

# -----------------------------------------------


# ------------------------------------
# -- INFO REQUEST CLASS-VIEWS --
# ------------------------------------
class Contact_View(SuccessMessageMixin, generic.CreateView):
    template_name = 'contact/form.html'
    model = InfoRequest_Model
    form_class = InfoRequest_Form
    success_message = "Thank you, %(name)s! Your request has been sent successfully. Check your email for more information!"

    # ENVIAR CORREO ELECTRONICO AL USUARIO, SI EL FORM ES VALIDO
    def form_valid(self, form):
        response = super().form_valid(form)
        # ENVIAMOS EL CORREO ELECTRONICO
        contact = form.instance
        subject = 'Request Received - Tiny Steps'
        message = render_to_string('contact/emails/confirmation.txt', {
            'name': contact.name,
        })
        send_mail(
            subject,
            message,
            'c4relecloud@gmail.com',
            [contact.email],
            fail_silently=False,
        )
        return response

# ------------------------------------

# ------------------------------------
# -- NOTIFICATIONS FUNCTION-BASED VIEWS --
# ------------------------------------
@receiver(post_save, sender=Comment_Model)
def notify_post_author_of_new_comment(sender, instance, created, **kwargs):
    if created and hasattr(instance.content_object, 'author'):
        post_author = instance.content_object.author
        if post_author != instance.author and post_author.email:
            post_title = instance.content_object.title if hasattr(instance.content_object, 'title') else 'your content'
            
            send_mail(
                f'New comment on {post_title}',
                f'{instance.author.username} commented: "{instance.text[:100]}..."',
                settings.DEFAULT_FROM_EMAIL,
                [post_author.email],
                fail_silently=True,
            )