from django.urls import path

class GuideService_Factory:
    """Factory for guide-related services"""
    @staticmethod
    def create_service(guide_type):
        """Create a guide service instance for the given type"""
        from tinySteps.registry import GuideType_Registry
        service_class = GuideType_Registry.get_service_class(guide_type)
        if not service_class:
            raise ValueError(f"No service class registered for guide type: {guide_type}")
        
        return service_class()

class GuideUrl_Factory:
    @staticmethod
    def create_urls(guide_type=None):
        """Crea patrones de URL para guías, opcionalmente por tipo"""
        from tinySteps.views.guides import guide_views, article_views, submission_views
        
        if guide_type:
            # URLs específicas por tipo de guía
            url_patterns = [
                # Vista de lista de guías
                path(f'guides/{guide_type}/', 
                    guide_views.guide_list_view, 
                    {'guide_type': guide_type}, 
                    name=f'{guide_type}_guides'),
                
                # Vista de detalle de guía
                path(f'guides/{guide_type}/<int:pk>/', 
                    guide_views.guide_detail_view, 
                    {'guide_type': guide_type}, 
                    name=f'{guide_type}_guide_details'),
                
                # Enviar guía por tipo
                path(f'guides/{guide_type}/submit/', 
                    submission_views.SubmitGuide_View.as_view(), 
                    {'guide_type': guide_type}, 
                    name=f'submit_{guide_type}_guide'),
            ]
            
            return url_patterns
        else:
            # URLs comunes para todas las guías
            return [
                # Página principal de guías
                path('guides/', guide_views.guides_page, name='guides'),
                
                # Formulario para enviar guía
                path('guides/submit/', submission_views.SubmitGuide_View.as_view(), name='submit_guide'),
                
                # Panel de administración de guías (si no se mueve a admin_factory)
                path('guides/admin-guides-panel/', guide_views.admin_guides_panel_view, name='admin_guides_panel'),
            ]