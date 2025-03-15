import logging
from datetime import datetime, timedelta, date
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.messages.views import SuccessMessageMixin
from django.core.mail import send_mail
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db import models
from django.db.models import Q, Prefetch
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.http import Http404, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.translation import gettext as _
from django.views import View, generic
from django.views.generic.edit import CreateView

from .forms import (
    Contact_Form, 
    Milestone_Form,
    PasswordReset_Form,
    CustomUserCreation_Form,
    YourChild_Form,
)
from .models import (
    Contact_Model, 
    YourChild_Model, 
    ParentsForum_Model,
    Guides_Model,
    ParentsGuides_Model,
    NutritionGuides_Model,
    Comment_Model,
    Like_Model,
    CalendarEvent_Model,
    VaccineCard_Model,
    Vaccine_Model,
)

# -----------------------------------------------
# -- GENERAL VIEWS
# -----------------------------------------------
def index(request):
    return render(request, 'pages/index.html')

def about(request):
    return render(request, 'pages/about.html')

def page_not_found(request, exception):
    return render(request, 'pages/404.html', status=404)

# -----------------------------------------------
# -- AUTHENTICATION VIEWS
# -----------------------------------------------
class Login_View(auth_views.LoginView):
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        return reverse_lazy('index')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, _("Login successful!"))
        return response
    
    def form_invalid(self, form):
        messages.error(self.request, _("Usuario o contraseña incorrectos. ¿No tienes cuenta? Regístrate ahora."))
        return super().form_invalid(form)
    
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('index')
        return super().get(request, *args, **kwargs)

class Logout_View(auth_views.LogoutView):
    next_page = 'index'
    
    def dispatch(self, request, *args, **kwargs):
        messages.success(request, _('You have been successfully logged out!'))
        return super().dispatch(request, *args, **kwargs)

class Register_View(CreateView):
    form_class = CustomUserCreation_Form
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('index')
    
    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        messages.success(self.request, _("Registration successful!"))
        return super().form_valid(form)
    
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('index')
        return super().get(request, *args, **kwargs)

# -----------------------------------------------
# -- USER PROFILE VIEWS
# -----------------------------------------------
@login_required
def profile(request):
    children = YourChild_Model.objects.filter(user=request.user)
    forum_posts = ParentsForum_Model.objects.filter(author=request.user)\
        .annotate(comments_count=models.Count('comments'))\
        .order_by('-created_at')
    
    context = {
        'children': children,
        'forum_posts': forum_posts[:5],
    }
    
    return render(request, 'accounts/profile.html', context)

def password_reset(request):
    if request.method == 'POST':
        form = PasswordReset_Form(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            user = User.objects.get(username=username)
            
            password = form.cleaned_data['new_password1']
            user.set_password(password)
            user.save()
            
            messages.success(request, _("Your password has been updated successfully! You can now log in."))
            return redirect('login')
    else:
        form = PasswordReset_Form()
    
    return render(request, 'accounts/user_password/reset_password.html', {'form': form})

# -----------------------------------------------
# -- CHILDREN VIEWS
# -----------------------------------------------
@login_required(login_url='login')
def your_children(request):
    children = YourChild_Model.objects.filter(user=request.user)
    return render(request, 'children/list.html', {'children': children})

@login_required(login_url='login')
def your_child(request, pk):
    child = get_object_or_404(YourChild_Model, pk=pk)
    return render(request, 'children/detail.html', {'child': child})

class YourChild_Add_View(LoginRequiredMixin, SuccessMessageMixin, generic.CreateView):
    login_url = 'login'
    template_name = 'children/actions/create.html'
    model = YourChild_Model
    form_class = YourChild_Form
    success_url = reverse_lazy('your_children')
    success_message = _("Child added successfully!")

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class YourChild_Delete_View(LoginRequiredMixin, SuccessMessageMixin, generic.DeleteView):
    login_url = 'login'
    template_name = 'children/actions/delete.html'
    model = YourChild_Model
    success_url = reverse_lazy('your_children')
    success_message = _("Child removed successfully!")
    
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
    
    def child_has_events(self):
        return CalendarEvent_Model.objects.filter(child=self.get_object()).exists()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['has_events'] = self.child_has_events()
        return context

class YourChild_UpdateDetails_View(LoginRequiredMixin, SuccessMessageMixin, generic.UpdateView):
    login_url = 'login'
    template_name = 'children/actions/edit.html'
    model = YourChild_Model
    form_class = YourChild_Form
    success_message = _("Child information updated successfully!")
    
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
        self.object.refresh_from_db()
        
        messages.success(self.request, _("Child information updated successfully!"))
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('child_details', kwargs={'pk': self.object.pk})

# -----------------------------------------------
# -- CHILD FEATURES VIEWS
# -----------------------------------------------
@login_required
def child_milestone(request, child_id):
    child = get_object_or_404(YourChild_Model, id=child_id, user=request.user)
    
    if request.method == 'POST':
        form = Milestone_Form(request.POST, request.FILES)
        if form.is_valid():
            milestone = form.save(commit=False)
            milestone.child = child
            milestone.save()
            messages.success(request, _("Milestone added!"))
            return redirect('your_child', pk=child_id)
    else:
        form = Milestone_Form()
    
    return render(request, 'children/features/milestones/index.html', {
        'form': form, 
        'child': child,
        'today': timezone.now().date()
    })

@login_required
def child_calendar(request, child_id):
    child = get_object_or_404(YourChild_Model, id=child_id, user=request.user)
    
    event_stats = {
        'doctor': CalendarEvent_Model.objects.filter(child=child, type='doctor').count(),
        'vaccine': CalendarEvent_Model.objects.filter(child=child, type='vaccine').count(),
        'milestone': CalendarEvent_Model.objects.filter(child=child, type='milestone').count(),
        'feeding': CalendarEvent_Model.objects.filter(child=child, type='feeding').count(),
        'other': CalendarEvent_Model.objects.filter(child=child, type='other').count(),
    }
    
    upcoming_reminders = CalendarEvent_Model.objects.filter(
        child=child, 
        has_reminder=True,
        date__gte=date.today()
    ).order_by('date', 'time')[:5]

    upcoming_events = CalendarEvent_Model.objects.filter(
        child=child,
        date__gte=date.today()
    ).order_by('date', 'time')[:5]

    context = {
        'child': child,
        'event_stats': event_stats,
        'upcoming_reminders': upcoming_reminders,
        'upcoming_events': upcoming_events,
    }
    
    return render(request, 'children/features/calendar/index.html', context)

@login_required
def child_vaccine_card(request, child_id):
    child = get_object_or_404(YourChild_Model, id=child_id, user=request.user)
    
    # Obtener o crear la cartilla de vacunación
    vaccine_card, created = VaccineCard_Model.objects.get_or_create(child=child)
    
    # Obtener todas las vacunas
    vaccines = Vaccine_Model.objects.filter(vaccine_card=vaccine_card).order_by('next_dose_date', 'date')
    
    # Estadísticas
    total_vaccines = vaccines.count()
    administered_vaccines = vaccines.filter(administered=True).count()
    pending_vaccines = total_vaccines - administered_vaccines
    
    # Vacunas próximas (con fecha de próxima dosis en el próximo mes)
    today = date.today()
    next_month = today + timedelta(days=30)
    upcoming_vaccines = vaccines.filter(
        next_dose_date__gte=today,
        next_dose_date__lte=next_month
    ).count()
    
    upcoming_vaccines_list = vaccines.filter(
        next_dose_date__gte=today
    ).order_by('next_dose_date')[:5]

    context = {
        'child': child,
        'vaccine_card': vaccine_card,
        'vaccines': vaccines,
        'total_vaccines': total_vaccines,
        'administered_vaccines': administered_vaccines,
        'pending_vaccines': pending_vaccines,
        'upcoming_vaccines': upcoming_vaccines,
        'upcoming_vaccines_list': upcoming_vaccines_list,
    }
    
    return render(request, 'children/features/vaccine-card/index.html', context)

class YourChild_Calendar_View(LoginRequiredMixin, View):
    template_name = 'children/features/calendar/index.html'
    
    def get(self, request, pk):
        child = get_object_or_404(YourChild_Model, id=pk, user=request.user)
        events = CalendarEvent_Model.objects.filter(child=child).order_by('date', 'time')
        
        today = datetime.now().date()
        week_later = today + timedelta(days=7)
        
        # Filtrar eventos para recordatorios
        upcoming_reminders = events.filter(
            date__gte=today,
            date__lte=week_later,
            has_reminder=True
        ).order_by('date', 'time')
        
        # Filtrar próximos eventos (todos, no solo con recordatorios)
        upcoming_events = events.filter(
            date__gte=today,
            date__lte=week_later
        ).order_by('date', 'time')
        
        event_stats = {
            'doctor': events.filter(type='doctor').count(),
            'vaccine': events.filter(type='vaccine').count(),
            'milestone': events.filter(type='milestone').count(),
            'feeding': events.filter(type='feeding').count(),
            'other': events.filter(type='other').count(),
        }
        
        return render(request, self.template_name, {
            'child': child,
            'events': events,
            'upcoming_reminders': upcoming_reminders,
            'upcoming_events': upcoming_events,
            'event_stats': event_stats
        })

class YourChild_VaccineCard_View(LoginRequiredMixin, generic.DetailView):
    login_url = 'login'
    template_name = 'children/features/vaccine-card/index.html'
    model = YourChild_Model
    context_object_name = 'child'
    
    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)
    
    def get_object(self, queryset=None):
        obj = super().get_object()
        if not obj.user == self.request.user:
            raise Http404
        return obj
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        vaccine_card, created = VaccineCard_Model.objects.get_or_create(child=self.object)
        context['vaccine_card'] = vaccine_card
        
        vaccines = Vaccine_Model.objects.filter(vaccine_card=vaccine_card).order_by('next_dose_date', 'date')
        context['vaccines'] = vaccines
        
        # Statistics
        context['total_vaccines'] = vaccines.count()
        context['administered_vaccines'] = vaccines.filter(administered=True).count()
        context['pending_vaccines'] = context['total_vaccines'] - context['administered_vaccines']
        
        # Upcoming vaccines
        today = date.today()
        next_month = today + timedelta(days=30)
        context['upcoming_vaccines'] = vaccines.filter(
            next_dose_date__gte=today,
            next_dose_date__lte=next_month
        ).count()
        
        context['upcoming_vaccines_list'] = vaccines.filter(
            next_dose_date__gte=today
        ).order_by('next_dose_date')[:5]
        
        return context

# -----------------------------------------------
# -- FORUM VIEWS
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

    # Filtering
    query = request.GET.get('search')
    if query:
        posts_list = posts_list.filter(title__icontains=query)
        
    category = request.GET.get('category')
    if category:
        posts_list = posts_list.filter(category=category)
    
    # Sorting
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
    
    # Pagination
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
    """Redirects to parents_forum_page with search parameters"""
    search_query = request.GET.get('search', '')
    category = request.GET.get('category', '')
    
    redirect_url = reverse_lazy('parents_forum')
    if search_query or category:
        redirect_url += f"?search={search_query}"
        if category:
            redirect_url += f"&category={category}"
    
    return redirect(redirect_url)

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
            messages.success(request, _("Post created successfully!"))
            return redirect('view_post', post_id=post.id)
        else:
            messages.error(request, _("Please fill all required fields"))
    
    return render(request, 'forum/posts/create.html')

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
                messages.success(request, _("Post updated successfully!"))
                return redirect('view_post', post_id=post.id)
            else:
                messages.error(request, _("Please fill all required fields"))
        
        return render(request, 'forum/posts/edit.html', {'post': post})
    else:
        messages.error(request, _("You don't have permission to edit this post"))
        return redirect('parents_forum')

@login_required
def delete_post(request, post_id):
    post = get_object_or_404(ParentsForum_Model, id=post_id)
    
    if request.user == post.author or request.user.is_staff or request.user.is_superuser:
        if request.method == 'POST':
            post.delete()
            messages.success(request, _("Post deleted successfully!"))
            return redirect('parents_forum')
        
        return render(request, 'forum/posts/delete.html', {'post': post})
    else:
        messages.error(request, _("You don't have permission to delete this post"))
        return redirect('parents_forum')

# -----------------------------------------------
# -- INTERACTION VIEWS (COMMENTS & LIKES)
# -----------------------------------------------
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
            messages.success(request, _("Comment added successfully!"))
        else:
            messages.error(request, _("Please enter a comment."))
    
    return redirect('view_post', post_id=post.id)

def add_comment(request, model_type, pk):
    if model_type == 'forum':
        obj = get_object_or_404(ParentsForum_Model, pk=pk)
    elif model_type == 'parent_guide':
        obj = get_object_or_404(ParentsGuides_Model, pk=pk)
    elif model_type == 'nutrition_guide':
        obj = get_object_or_404(NutritionGuides_Model, pk=pk)
    else:
        raise Http404(_("Invalid content type"))
    
    if request.method == 'POST':
        text = request.POST.get('text')
        if text:
            Comment_Model.objects.create(
                content_object=obj,
                author=request.user,
                text=text
            )
            messages.success(request, _("Comentario añadido correctamente."))
        return redirect(obj.get_absolute_url())

@login_required
def forum_post_like_toggle(request, post_id):
    """
    Toggle like status for forum posts
    """
    content_type = ContentType.objects.get_for_model(ParentsForum_Model)
    return like_toggle(request, content_type.id, post_id)

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
            Like_Model.objects.filter(
                content_type=content_type,
                object_id=object_id,
                user=request.user
            ).delete()
            liked = False
        else:
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
            'message': _('An error occurred processing your request')
        }, status=400)

# -----------------------------------------------
# -- GUIDES VIEWS
# -----------------------------------------------
def guides_page(request):
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
# -- CONTACT VIEWS
# -----------------------------------------------
class Contact_View(SuccessMessageMixin, generic.CreateView):
    template_name = 'contact/form.html'
    model = Contact_Model
    form_class = Contact_Form
    success_message = _("Thank you, %(name)s! Your request has been sent successfully. Check your email for more information!")

    def form_valid(self, form):
        response = super().form_valid(form)
        contact = form.instance
        subject = _('Request Received - Tiny Steps')
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

# -----------------------------------------------
# -- NOTIFICATIONS
# -----------------------------------------------
@receiver(post_save, sender=Comment_Model)
def notify_post_author_of_new_comment(sender, instance, created, **kwargs):
    if created and hasattr(instance.content_object, 'author'):
        post_author = instance.content_object.author
        if post_author != instance.author and post_author.email:
            post_title = instance.content_object.title if hasattr(instance.content_object, 'title') else _('your content')
            
            send_mail(
                _('New comment on {0}').format(post_title),
                _("{0} commented: \"{1}...\"").format(instance.author.username, instance.text[:100]),
                settings.DEFAULT_FROM_EMAIL,
                [post_author.email],
                fail_silently=True,
            )
