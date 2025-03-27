import logging
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.translation import gettext as _
from django.conf import settings

from tinySteps.models import Contact_Model

logger = logging.getLogger(__name__)

class Contact_Service:
    """Service for contact functionality"""
    
    def save_contact_request(self, form_data):
        """Save contact request and send confirmation email"""
        # Here we create and save contact model
        contact = Contact_Model.objects.create(
            name=form_data['name'],
            email=form_data['email'],
            message=form_data['message']
        )
        
        self._send_confirmation_email(contact)
        return contact
    
    def _send_confirmation_email(self, contact):
        """Send confirmation email to the contact"""
        subject = _('Request Received - Tiny Steps')
        message = render_to_string('contact/emails/confirmation.txt', {
            'name': contact.name,
        })
        
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'c4relecloud@gmail.com')
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