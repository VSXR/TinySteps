from django.contrib import messages
from django.utils.translation import gettext as _
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy

from tinySteps.models import YourChild_Model
from tinySteps.forms import YourChild_Form

class YourChild_Add_View(LoginRequiredMixin, CreateView):
    """View to add a new child"""
    model = YourChild_Model
    form_class = YourChild_Form
    template_name = 'children/actions/create.html'
    
    def form_valid(self, form):
        """Set the user before saving the form"""
        form.instance.user = self.request.user
        messages.success(self.request, _("Child added successfully!"))
        return super().form_valid(form)
    
    def get_success_url(self):
        """Redirect to the child details page after successful creation"""
        return reverse_lazy('children:child_detail', kwargs={'child_id': self.object.pk})

class YourChild_UpdateDetails_View(LoginRequiredMixin, UpdateView):
    """View to update child details"""
    model = YourChild_Model
    form_class = YourChild_Form
    template_name = 'children/actions/edit.html'
    
    def get_success_url(self):
        """Return to the child details page after updating"""
        return reverse_lazy('children:child_detail', kwargs={'child_id': self.object.pk})

    def get_queryset(self):
        """Ensure users can only edit their own children"""
        return YourChild_Model.objects.filter(user=self.request.user)
    
    def form_valid(self, form):
        """Handle successful form submission"""
        messages.success(self.request, _("Child details updated successfully!"))
        return super().form_valid(form)
    
class YourChild_Delete_View(LoginRequiredMixin, DeleteView):
    """View to delete a child"""
    model = YourChild_Model
    template_name = 'children/actions/delete.html'
    success_url = reverse_lazy('children:your_children')
    
    def get_queryset(self):
        """Ensure users can only delete their own children"""
        return YourChild_Model.objects.filter(user=self.request.user)
    
    def delete(self, request, *args, **kwargs):
        """Custom delete method with success message"""
        messages.success(self.request, _("Child deleted successfully."))
        return super().delete(request, *args, **kwargs)