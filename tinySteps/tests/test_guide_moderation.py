from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone

# Ajusta las importaciones según tu estructura
from tinySteps.models.content.guide_models import Guides_Model
from tinySteps.services.guides.moderation_service import GuideModeration_Service

class GuideModeration_ServiceTests(TestCase):
    """Tests para el servicio de moderación de guías"""
    
    def setUp(self):
        # Crear un usuario de prueba
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass',
            email='test@example.com'
        )
        
        # Crear un usuario moderador
        self.moderator = User.objects.create_user(
            username='moderator',
            password='modpass',
            email='mod@example.com',
            is_staff=True
        )
        
        # Crear una guía de prueba
        self.guide = Guides_Model.objects.create(
            title='Guía de Prueba',
            desc='Esta es una descripción de guía de prueba',
            author=self.user,
            guide_type='parent',
            status='pending'
        )
        
        # Inicializar el servicio
        self.service = GuideModeration_Service()
    
    def test_get_guide(self):
        """Probar recuperación de guía por ID"""
        guide = self.service.get_guide(self.guide.id)
        self.assertEqual(guide.id, self.guide.id)
        self.assertEqual(guide.title, 'Guía de Prueba')
    
    def test_get_guide_nonexistent(self):
        """Probar comportamiento cuando la guía no existe"""
        with self.assertRaises(ValueError):
            self.service.get_guide(999999)
    
    def test_approve_guide(self):
        """Probar aprobación de guía"""
        guide = self.service.approve_guide(self.guide.id, self.moderator)
        
        # Recargar desde la DB para obtener los valores más recientes
        guide.refresh_from_db()
        
        self.assertEqual(guide.status, 'approved')
        self.assertIsNotNone(guide.approved_at)
        self.assertIsNotNone(guide.published_at)
        self.assertEqual(guide.moderated_by, self.moderator)
        self.assertIsNotNone(guide.moderation_date)
    
    def test_reject_guide(self):
        """Probar rechazo de guía"""
        rejection_reason = "El contenido no es lo suficientemente detallado"
        guide = self.service.reject_guide(self.guide.id, rejection_reason, self.moderator)
        
        # Recargar desde la DB para obtener los valores más recientes
        guide.refresh_from_db()
        
        self.assertEqual(guide.status, 'rejected')
        self.assertEqual(guide.rejection_reason, rejection_reason)
        self.assertEqual(guide.moderated_by, self.moderator)
        self.assertIsNotNone(guide.moderation_date)