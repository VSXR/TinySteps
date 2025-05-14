import logging
import json
from typing import Optional, Dict, Any
from django.utils import timezone


class AuditLogger:
    """Logger for system audit actions with standardized logging formats."""
    
    def __init__(self):
        """Initialize the audit logger."""
        self.logger = logging.getLogger('audit')
    
    def _format_log_data(self, entity_type: str, entity_id: Optional[str], 
                         entity_name: str, action: str, actor: str, 
                         details: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Format log data in a consistent structure."""
        return {
            'timestamp': timezone.now().isoformat(),
            'entity_type': entity_type,
            'entity_id': entity_id,
            'entity_name': entity_name,
            'action': action,
            'actor': actor,
            'details': details or {}
        }
    
    def log_action(self, actor: str, action: str, resource_id: Optional[str] = None, 
                  resource_type: Optional[str] = None, message: Optional[str] = None) -> None:
        """Log a system action for audit purposes."""
        details = {'message': message} if message else {}
        
        log_data = self._format_log_data(
            entity_type=resource_type or 'system',
            entity_id=resource_id,
            entity_name=resource_id or '',
            action=action,
            actor=actor,
            details=details
        )
        
        self.logger.info(f"AUDIT:{json.dumps(log_data)}")
        print(f"AUDIT: {json.dumps(log_data)}")  # For development

    def log_moderation_action(self, guide_id: str, guide_title: str, 
                             action: str, moderator: Optional[str] = None, 
                             reason: Optional[str] = None) -> None:
        """Log a guide moderation action."""
        details = {'reason': reason or 'No proporcionado'}
        
        log_data = self._format_log_data(
            entity_type='guide',
            entity_id=guide_id,
            entity_name=guide_title,
            action=action,
            actor=moderator or 'system',
            details=details
        )
        
        self.logger.info(f"AUDIT:MODERATION:{json.dumps(log_data)}")
        
    def log_user_action(self, user_id: str, username: str, 
                       action: str, details: Optional[Dict[str, Any]] = None) -> None:
        """Log a user action."""
        log_data = self._format_log_data(
            entity_type='user',
            entity_id=user_id,
            entity_name=username,
            action=action,
            actor=username,
            details=details
        )
        
        self.logger.info(f"AUDIT:USER:{json.dumps(log_data)}")


# Add this alias for backward compatibility
Audit_Logger = AuditLogger