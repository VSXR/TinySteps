from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth import views as auth_views
from django.contrib.auth.forms import UserCreationForm
from django.contrib.messages.views import SuccessMessageMixin
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.views import generic
from django.views.generic.edit import CreateView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

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
    next_page = reverse_lazy('index')
    
    def get(self, request, *args, **kwargs):
        messages.success(self.request, "Logout successful!")
        return super().get(request, *args, **kwargs)

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
    forums_list = ParentsForum_Model.objects.all()
    
    # Búsqueda por título
    query = request.GET.get('search')
    if query:
        forums_list = forums_list.filter(title__icontains=query)
        
    # Filtrar por categoría
    category = request.GET.get('category')
    if category:
        forums_list = forums_list.filter(category=category)
    
    # Ordenar resultados
    sort = request.GET.get('sort', 'created_at')
    if sort == 'title':
        forums_list = forums_list.order_by('title')
    else:
        forums_list = forums_list.order_by('-created_at')
    
    # Paginación
    paginator = Paginator(forums_list, 10)  # 10 foros por página
    page = request.GET.get('page')
    forums = paginator.get_page(page)
    
    return render(request, 'parents_forum/parents_forum_page.html', {'forums': forums})

def parents_forum_details(request, pk):
    forum_details = get_object_or_404(ParentsForum_Model, pk=pk)
    # Marcar como visto
    if request.user.is_authenticated:
        Notification_Model.objects.filter(user=request.user, forum=forum_details).update(read=True)
    return render(request, 'parents_forum/forum_details.html', {'forum': forum_details})

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
