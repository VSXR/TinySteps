from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import mail_admins
from django.conf import settings
from django.utils.translation import gettext as _

# Ajusta la importación según tu estructura
from tinySteps.models.content.guide_models import Guides_Model

@receiver(post_save, sender=Guides_Model)
def guide_status_changed(sender, instance, created, **kwargs):
    """Manejador de señal para cambios de estado en guías"""
    if created:
        # Notificar a los admins sobre nueva guía sometida
        subject = _("Nueva Guía Enviada: {0}").format(instance.title)
        message = _("""
        Una nueva guía ha sido enviada y requiere tu revisión:
        
        Título: {title}
        Tipo: {guide_type}
        Autor: {author}
        
        Por favor revísala en: {site_url}/admin/tinySteps/guides_model/{id}/change/
        """).format(
            title=instance.title,
            guide_type=instance.get_guide_type_display(),
            author=f"{instance.author.get_full_name()} ({instance.author.username})",
            site_url=settings.SITE_URL if hasattr(settings, 'SITE_URL') else 'https://tinysteps.com',
            id=instance.id
        )
        
        try:
            mail_admins(subject, message, fail_silently=True)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error al enviar email a los administradores: {str(e)}")