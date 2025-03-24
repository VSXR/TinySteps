import logging
from django.views import generic
from django.contrib.messages.views import SuccessMessageMixin
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.translation import gettext as _
from django.conf import settings
from ..models import Contact_Model
from ..forms import Contact_Form

logger = logging.getLogger(__name__)

class Contact_View(SuccessMessageMixin, generic.CreateView):
    template_name = 'contact/form.html'
    model = Contact_Model
    form_class = Contact_Form
    success_url = reverse_lazy('contact')
    success_message = _("Thank you, %(name)s! Your request has been sent successfully. Check your email for more information!")

    def form_valid(self, form):
        response = super().form_valid(form)
        contact = form.instance
        
        subject = _('Request Received - Tiny Steps')
        message = render_to_string('contact/emails/confirmation.txt', {
            'name': contact.name,
        })
        
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'tinysteps@example.com')
        recipient_email = contact.email
        
        try:
            logger.debug(f"Sending email with: FROM: {from_email}, TO: {recipient_email}")
            logger.debug(f"SMTP Settings: HOST={settings.EMAIL_HOST}, PORT={settings.EMAIL_PORT}, USER={settings.EMAIL_HOST_USER}")
            
            send_mail(
                subject,
                message,
                from_email,
                [recipient_email],
                fail_silently=False,
            )
            
            logger.info(f"Confirmation email sent to {recipient_email}")
        except Exception as e:
            logger.error(f"Failed to send confirmation email: {str(e)}", exc_info=True)
        
        return response