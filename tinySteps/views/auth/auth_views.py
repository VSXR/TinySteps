from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.messages.views import SuccessMessageMixin
from django.db import models
from django.urls import reverse_lazy
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic.edit import CreateView

from tinySteps.forms import CustomUserCreation_Form, PasswordReset_Form
from tinySteps.models import PasswordReset_Model, YourChild_Model, ParentsForum_Model

class Login_View(auth_views.LoginView):
    """Login view"""
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True
    success_message = _("Login successful! Welcome back.")
    
    def get_success_url(self):
        """Override to add custom behavior for different user roles"""
        if self.request.user.is_staff:
            return reverse_lazy('admin:index')
        return reverse_lazy('index')
    
    def get(self, request, *args, **kwargs):
        """Handle GET requests for login page"""
        if request.user.is_authenticated:
            return redirect(self.get_success_url())
        return super().get(request, *args, **kwargs)
    
    @method_decorator(sensitive_post_parameters('password'))
    def post(self, request, *args, **kwargs):
        """Handle POST requests for login"""
        return super().post(request, *args, **kwargs)
    
    def form_valid(self, form):
        """Handle valid form submission"""
        messages.success(self.request, self.success_message)
        return super().form_valid(form)
    
    def form_invalid(self, form):
        """Handle invalid form submission"""
        messages.error(self.request, _("Login failed. Please check your credentials."))
        return super().form_invalid(form)

class Logout_View(auth_views.LogoutView):
    """Logout view"""
    next_page = 'index'
    
    def dispatch(self, request, *args, **kwargs):
        """We override the dispatch method to add a success message on logouts"""
        messages.success(request, _("You have been logged out successfully."))
        return super().dispatch(request, *args, **kwargs)

class Register_View(SuccessMessageMixin, CreateView):
    """User registration view"""
    template_name = 'accounts/register.html'
    form_class = CustomUserCreation_Form
    success_url = reverse_lazy('index')
    success_message = _("Account created successfully! You are now logged in.")
    
    def get(self, request, *_, **__):
        """Handle GET requests for registration page"""
        if request.user.is_authenticated:
            return redirect('index')
        return super().get(request)
    
    @method_decorator(sensitive_post_parameters('password1', 'password2'))
    def form_valid(self, form):
        """Handle valid form submission - log the user into TinySteps after registration"""
        response = super().form_valid(form)
        user = form.instance
        login(self.request, user)
        return response

@login_required
def profile(request):
    """User profile view"""
    children = YourChild_Model.objects.filter(user=request.user)
    forum_posts = ParentsForum_Model.objects.filter(author=request.user)\
        .annotate(comments_count=models.Count('comments'))\
        .order_by('-created_at')
    
    context = {
        'children': children,
        'forum_posts': forum_posts[:5],
    }
    
    return render(request, 'accounts/profile.html', context)

@login_required
def edit_profile(request):
    """Edit profile view"""
    if request.method == 'POST':
        form = CustomUserCreation_Form(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, _("Profile updated successfully!"))
            return redirect('profile')
    else:
        form = CustomUserCreation_Form(instance=request.user)
    
    return render(request, 'accounts/edit_profile.html', {'form': form})

@login_required
def password_reset(request):
    """Password reset view"""
    if request.method == 'POST':
        form = PasswordReset_Form(request.POST)
        if form.is_valid():
            user = User.objects.get(username=form.cleaned_data['username'])
            user.set_password(form.cleaned_data['new_password1'])
            user.save()
            
            PasswordReset_Model.objects.filter(user=user, is_used=False).update(is_used=True)
            messages.success(request, _("Password reset successfully! You can now login with your new password."))
            return redirect('login')
    else:
        form = PasswordReset_Form()
    
    return render(request, 'accounts/reset.html', {'form': form})