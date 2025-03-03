# Django core imports
from django.contrib import messages
from django.contrib.auth import login, views as auth_views
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.contenttypes.models import ContentType
from django.contrib.messages.views import SuccessMessageMixin
from django.core.mail import send_mail
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.views import generic
from django.views.generic.edit import CreateView

# LOCAL IMPORTS
from .forms import InfoRequest_Form, Milestone_Form
from .models import (
    InfoRequest_Model, 
    YourChild_Model, 
    ParentsForum_Model, 
    ParentsGuides_Model, 
    NutritionGuides_Model,
    Comment_Model,
    Milestone_Model,
    Notification_Model,
)

# -----------------------------------------------
# -- GENERAL FUNCTION-BASED VIEWS --
# -----------------------------------------------
def index(request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'about.html')

def page_not_found(request, exception):
    return render(request, '404.html', status=404)
# -----------------------------------------------


# -----------------------------------------------
# -- LOGIN, LOGOUT AND REGISTER CLASS-VIEWS --
# -----------------------------------------------
class Login_View(auth_views.LoginView):
    template_name = 'user_accounts/users/login_page.html'
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
    form_class = UserCreationForm
    template_name = 'user_accounts/users/register_page.html'
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
def dashboard(request):
    children = YourChild_Model.objects.filter(user=request.user)
    recent_forums = ParentsForum_Model.objects.all().order_by('-created_at')[:5]
    recent_guides = ParentsGuides_Model.objects.all().order_by('-created_at')[:5]
    
    return render(request, 'dashboard.html', {
        'children': children,
        'recent_forums': recent_forums,
        'recent_guides': recent_guides
    })
# -----------------------------------------------


# -----------------------------------------------
# -- YOUR_CHILDREN FUNCTION-BASED VIEWS --
# -----------------------------------------------
@login_required(login_url='login')
def your_children(request):
    children = YourChild_Model.objects.filter(user=request.user)
    return render(request, 'your_children/your_children_page.html', {'children': children})

@login_required(login_url='login')
def your_child(request, pk):
    child = get_object_or_404(YourChild_Model, pk=pk)
    return render(request, 'your_children/child_detail.html', {'child': child})

@login_required
def add_milestone(request, child_id):
    child = get_object_or_404(YourChild_Model, id=child_id, user=request.user)
    
    if request.method == 'POST':
        form = Milestone_Form(request.POST, request.FILES)
        if form.is_valid():
            milestone = form.save(commit=False)
            milestone.child = child
            milestone.save()
            messages.success(request, "Milestone added!")
            return redirect('child_details', pk=child_id)
    else:
        form = Milestone_Form()
    
    return render(request, 'your_children/add_milestone.html', {'form': form, 'child': child})

# -----------------------------------------------
# -- YOUR CHILDREN CLASS-VIEWS --
# -----------------------------------------------
class YourChild_Add_View(LoginRequiredMixin, SuccessMessageMixin, generic.CreateView):
    login_url = 'login'
    template_name = 'your_children/child_create.html'
    model = YourChild_Model
    fields = ['name', 'second_name', 'birth_date', 'image_url', 'age', 'weight', 'height', 'gender', 'desc']
    success_url = reverse_lazy('your_children')
    success_message = "Child added successfully!"

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)
    
    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)
    
    def get_success_url(self):
        return reverse_lazy('your_children')

class YourChild_Delete_View(LoginRequiredMixin, SuccessMessageMixin, generic.DeleteView):
    login_url = 'login'
    template_name = 'your_children/child_confirm_delete.html'
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
    template_name = 'your_children/your_child_edit.html'
    model = YourChild_Model
    fields = ['name', 'age', 'gender', 'desc']
    success_url = reverse_lazy('your_children')
    success_message = "Child information updated successfully!"
    
    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)
    
    def get_object(self, queryset=None):
        obj = super().get_object()
        if not obj.user == self.request.user:
            raise Http404
        return obj
    
    def get_success_url(self):
        return reverse_lazy('your_children')

class YourChild_Calendar_View(LoginRequiredMixin, generic.DetailView):
    login_url = 'login'
    template_name = 'your_children/child_calendar.html'
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
    template_name = 'your_children/child_vaccine_card.html'
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
# -- PARENTS FORUM FUNCTION-BASED VIEWS --
# -----------------------------------------------
def parents_forum_page(request):
    posts_list = ParentsForum_Model.objects.all()
    
    # Búsqueda por título
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
    else:
        posts_list = posts_list.order_by('-created_at')
    
    # Paginación
    paginator = Paginator(posts_list, 10)
    page = request.GET.get('page')
    try:
        posts = paginator.get_page(page)
    except (PageNotAnInteger, EmptyPage):
        posts = paginator.page(1)
    
    return render(request, 'parents_forum/parents_forum_page.html', {'posts': posts})

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
    
    return render(request, 'parents_forum/parents_forum_page.html', {
        'posts': posts,
        'query': query
    })

@login_required
def start_post(request):
    """Vista para mostrar el formulario de creación de un post nuevo"""
    return render(request, 'parents_forum/views/forum_actions/start_post.html')

@login_required
def add_post(request):
    """Vista para procesar la creación de un nuevo post"""
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
            return redirect('start_post')
    
    return redirect('parents_forum')

@login_required
def edit_post(request, post_id):
    """Vista para editar un post existente"""
    post = get_object_or_404(ParentsForum_Model, id=post_id, author=request.user)
    
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
    
    return render(request, 'parents_forum/views/forum_actions/edit_post.html', {'post': post})

@login_required
def delete_post(request, post_id):
    """Vista para eliminar un post"""
    post = get_object_or_404(ParentsForum_Model, id=post_id, author=request.user)
    
    if request.method == 'POST':
        post.delete()
        messages.success(request, "Post deleted successfully!")
        return redirect('parents_forum')
    
    return render(request, 'parents_forum/views/forum_actions/delete_post.html', {'post': post})

def view_post(request, post_id):
    """Vista para ver un post específico y sus comentarios"""
    post = get_object_or_404(ParentsForum_Model, id=post_id)
    
    # Obtener posts relacionados (por ejemplo, del mismo autor o con tags similares)
    related_posts = ParentsForum_Model.objects.filter(author=post.author).exclude(id=post_id)[:4]
    
    return render(request, 'parents_forum/views/view_post.html', {
        'post': post,
        'related_posts': related_posts
    })

@login_required
def add_post_comment(request, post_id):
    """Vista para añadir un comentario a un post"""
    post = get_object_or_404(ParentsForum_Model, id=post_id)
    
    if request.method == 'POST':
        content = request.POST.get('content')
        
        if content:
            # Crear el comentario usando el sistema genérico de contenidos
            content_type = ContentType.objects.get_for_model(ParentsForum_Model)
            Comment_Model.objects.create(
                content_type=content_type,
                object_id=post.id,
                author=request.user,
                text=content
            )
            messages.success(request, "Comment added successfully!")
        else:
            messages.error(request, "Comment text is required")
            
    return redirect('view_post', post_id=post_id)

# -----------------------------------------------
# -- PARENTS FORUM CLASS-VIEWS --
# -----------------------------------------------
class ParentsForum_Add_View(LoginRequiredMixin, SuccessMessageMixin, generic.CreateView):
    login_url = 'login'
    template_name = 'parents_forums/forum_create.html'
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
    template_name = 'parents_forums/forum_update.html'
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
    template_name = 'parents_forums/forum_confirm_delete.html'
    model = ParentsForum_Model
    success_url = reverse_lazy('parents_forum')
    success_message = "Forum deleted successfully!"
    
    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        messages.success(self.request, self.success_message)
        return response
    
    def get_queryset(self):
        return super().get_queryset().filter(author=self.request.user)
    
    def get_object(self, queryset=None):
        obj = super().get_object()
        if not obj.author == self.request.user:
            raise Http404
        return obj
    
    def get_success_url(self):
        return reverse_lazy('parents_forum')
# -----------------------------------------------


# -----------------------------------------------
# -- GUIDES FUNCTION-BASED VIEWS --
# -----------------------------------------------
# PAGINA GENERAL DE GUIAS
def guides_page(request):
    parents_guides = ParentsGuides_Model.objects.all()
    nutrition_guides = NutritionGuides_Model.objects.all()
    return render(request, 'guides/guides_page.html', {
        'parents_guides': parents_guides,
        'nutrition_guides': nutrition_guides
    })

# PAGINA DE GUIAS PARA PADRES
def parents_guides_page(request):
    parents_guides = ParentsGuides_Model.objects.all()
    return render(request, 'guides/views/parents_guides/parents_guides.html', {'parents_guides': parents_guides})

def parent_guide_details(request, pk):
    guide = get_object_or_404(ParentsGuides_Model, pk=pk)
    return render(request, 'guides/views/parents_guides/view_parent_guide.html', {'guide': guide})

# PAGINA DE GUIAS DE NUTRICION
def nutrition_guides_page(request):
    nutrition_guides = NutritionGuides_Model.objects.all()
    return render(request, 'guides/views/nutrition_guides/nutrition_guides.html', {'nutrition_guides': nutrition_guides})

def nutrition_guide_details(request, pk):
    guide = get_object_or_404(NutritionGuides_Model, pk=pk)
    return render(request, 'guides/views/nutrition_guides/view_nutrition_guide.html', {'guide': guide})
# -----------------------------------------------


# ------------------------------------
# -- INFO REQUEST CLASS-VIEWS --
# ------------------------------------
class InfoRequestCreate(SuccessMessageMixin, generic.CreateView):
    template_name = 'info_request_create.html'
    model = InfoRequest_Model
    form_class = InfoRequest_Form
    success_message = "Thank you, %(name)s! Your request has been sent successfully. Check your email for more information!"

    # ENVIAR CORREO ELECTRONICO AL USUARIO, SI EL FORM ES VALIDO
    def form_valid(self, form):
        response = super().form_valid(form)
        # ENVIAMOS EL CORREO ELECTRONICO
        info_request = form.instance
        subject = 'Info Request Received'
        message = render_to_string('info_request_email.txt', {
            'name': info_request.name,
        })
        send_mail(
            subject,
            message,
            'c4relecloud@gmail.com',
            [info_request.email],
            fail_silently=False,
        )
        return response
