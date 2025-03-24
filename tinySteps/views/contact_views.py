from django.views import generic
from django.contrib.messages.views import SuccessMessageMixin
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.translation import gettext as _
from ..models import Contact_Model
from ..forms import Contact_Form

class Contact_View(SuccessMessageMixin, generic.CreateView):
    template_name = 'contact/form.html'
    model = Contact_Model
    form_class = Contact_Form
    success_url = reverse_lazy('contact:thanks')  # Add this if not defined in model
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
