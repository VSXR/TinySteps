import logging
import json
from django.utils import timezone

class Audit_Logger:
    """Logger para acciones de auditoría en el sistema"""
    
    def __init__(self):
        self.logger = logging.getLogger('audit')
    
    def log_moderation_action(self, guide_id, guide_title, action, moderator=None, reason=None):
        """Registrar una acción de moderación de guías"""
        log_data = {
            'timestamp': timezone.now().isoformat(),
            'entity_type': 'guide',
            'entity_id': guide_id,
            'entity_name': guide_title,
            'action': action,
            'actor': moderator or 'system',
            'reason': reason or 'No proporcionado'
        }
        
        self.logger.info(f"AUDIT:MODERATION:{json.dumps(log_data)}")
        
    def log_user_action(self, user_id, username, action, details=None):
        """Registrar una acción de usuario"""
        log_data = {
            'timestamp': timezone.now().isoformat(),
            'entity_type': 'user',
            'entity_id': user_id,
            'entity_name': username,
            'action': action,
            'details': details or {}
        }
        
        self.logger.info(f"AUDIT:USER:{json.dumps(log_data)}")