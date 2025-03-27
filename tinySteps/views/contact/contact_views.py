from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages
from django.utils.translation import gettext as _

from tinySteps.forms.communication.contact_forms import Contact_Form
from tinySteps.services.communication.contact_service import Contact_Service

class Contact_View(View):
    """View for handling contact form"""
    
    def get(self, request):
        """Display contact form"""
        form = Contact_Form()
        return render(request, 'contact/form.html', {'form': form})
    
    def post(self, request):
        """Process contact form submission"""
        form = Contact_Form(request.POST)
        
        if form.is_valid():
            service = Contact_Service()
            service.save_contact_request(form.cleaned_data)
            messages.success(request, _("Thank you for contacting us! We'll respond shortly."))
            return redirect('contact')
        
        return render(request, 'contact/form.html', {'form': form})