from django.shortcuts import render, redirect
from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages
from django.utils.translation import gettext as _
from django.core.mail import send_mail
from django.conf import settings

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
            
            # Send confirmation email
            name = form.cleaned_data.get('name', '')
            email = form.cleaned_data.get('email', '')
            message_content = form.cleaned_data.get('message', '')
            
            subject = f"Contact form submission from {name}"
            message = f"From: {email}\n\nMessage: {message_content}"
            from_email = settings.DEFAULT_FROM_EMAIL
            recipient_list = [email]  # Send to the user who submitted the form
            
            send_mail(
                subject,
                message,
                from_email,
                recipient_list,
                fail_silently=False,
            )
            
            messages.success(request, _("Thank you for contacting us! We'll respond shortly."))
            return redirect('contact')
        
        return render(request, 'contact/form.html', {'form': form})
    
def contact_success(request):
    pass