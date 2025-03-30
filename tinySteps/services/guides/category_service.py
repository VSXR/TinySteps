from tinySteps.models import Category_Model, ParentsGuides_Model, NutritionGuides_Model
from django.db.models import Count

class Category_Service:
    """Service for category management"""
    
    def get_all_categories(self):
        """Get all categories"""
        return Category_Model.objects.all().order_by('name')
    
    def get_category_by_id(self, category_id):
        """Get a category by ID"""
        try:
            return Category_Model.objects.get(id=category_id)
        except Category_Model.DoesNotExist:
            return None
    
    def get_guide_categories(self, guide_type='parent'):
        """Get categories that have guides of the specified type"""
        if guide_type == 'parent':
            # Get all parent guides
            guides = ParentsGuides_Model.objects.filter(
                guide_type='parent',
                status='approved'
            )
        else:
            # Get all nutrition guides
            guides = NutritionGuides_Model.objects.filter(
                guide_type='nutrition',
                status='approved'
            )
        
        # Get the category IDs used by these guides
        category_ids = guides.values_list('category_id', flat=True).distinct()
        
        # Get the categories and annotate with counts
        categories = Category_Model.objects.filter(
            id__in=category_ids
        ).annotate(
            article_count=Count('parentsguides_model')
        ).order_by('name')
        
        return categories
    
    def get_nested_categories(self):
        """Get categories in a nested structure"""
        # Get all top-level categories (no parent)
        top_level = Category_Model.objects.filter(parent=None).order_by('name')
        
        result = []
        for category in top_level:
            category_data = {
                'id': category.id,
                'name': category.name,
                'children': []
            }
            
            # Get children for this category
            children = Category_Model.objects.filter(parent=category).order_by('name')
            for child in children:
                category_data['children'].append({
                    'id': child.id,
                    'name': child.name
                })
            
            result.append(category_data)
        
        return result