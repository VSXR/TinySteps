from django.conf import settings

class Guide_ViewHelper:
    """Helper class for guide views"""
    
    @staticmethod
    def get_template(guide_type, view_type):
        """Return the appropriate template path based on guide type and view type"""
        base_dir = "guides"
        
        template_map = {
            'parent': {
                'list': f"{base_dir}/parent_guides.html",
                'detail': f"{base_dir}/parent_guide_detail.html",
                'form': f"{base_dir}/submit_parent_guide.html",
            },
            'nutrition': {
                'list': f"{base_dir}/nutrition_guides.html",
                'detail': f"{base_dir}/nutrition_guide_detail.html",
                'form': f"{base_dir}/submit_nutrition_guide.html",
            }
        }
        
        # Default to parent guide templates if type not found
        guide_templates = template_map.get(guide_type, template_map['parent'])
        
        # Default to list template if view type not found
        return guide_templates.get(view_type, guide_templates['list'])
    
    @staticmethod
    def enhance_context(context, guide_type, request=None):
        """Add type-specific data to the context"""
        # Add guide type to context
        context['guide_type'] = guide_type
        context['guide_title'] = guide_type.capitalize() + " Guides"
        
        # Add type-specific sidebar items
        if guide_type == 'parent':
            context['sidebar_items'] = [
                {'title': 'Newborn Care', 'url': '/guides/parent/tag/newborn/'},
                {'title': 'Sleep Training', 'url': '/guides/parent/tag/sleep/'},
                {'title': 'Toddler Development', 'url': '/guides/parent/tag/toddler/'},
            ]
        elif guide_type == 'nutrition':
            context['sidebar_items'] = [
                {'title': 'Baby Food', 'url': '/guides/nutrition/tag/baby-food/'},
                {'title': 'Toddler Meals', 'url': '/guides/nutrition/tag/toddler-meals/'},
                {'title': 'Allergies', 'url': '/guides/nutrition/tag/allergies/'},
            ]
        
        # Add user's submitted guides if user is logged in
        if request and request.user.is_authenticated:
            from tinySteps.models import Guides_Model
            context['user_guides'] = Guides_Model.objects.filter(
                author=request.user,
                guide_type=guide_type
            ).order_by('-created_at')[:5]
        
        return context