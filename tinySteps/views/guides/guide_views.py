from django.contrib import messages
from django.shortcuts import render, redirect
from django.utils.translation import gettext as _
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from tinySteps.utils.helpers.guides_helper import Guide_ViewHelper
from tinySteps.factories import GuideService_Factory
from tinySteps.services.core.admin_service import AdminGuide_Service
from tinySteps.services.comments.comment_service import Comment_Service

view_helper = Guide_ViewHelper.create_default()

def guides_page(request):
    """Main guide landing page"""
    parent_service = GuideService_Factory.create_service('parent')
    nutrition_service = GuideService_Factory.create_service('nutrition')
    
    # Change 'limit' to 'count' in all these calls
    all_parent_guides = parent_service.get_recent_guides(count=3)
    all_nutrition_guides = nutrition_service.get_recent_guides(count=3)
    
    recent_parent_guides = parent_service.get_recent_guides(count=4)
    recent_nutrition_guides = nutrition_service.get_recent_guides(count=4)
    
    popular_parent_guides = parent_service.get_recent_guides(count=4)
    popular_nutrition_guides = nutrition_service.get_recent_guides(count=4)
    
    # Rest of the function remains the same
    is_staff = request.user.is_staff
    pending_guides_count = 0
    if is_staff:
        admin_service = AdminGuide_Service()
        pending_guides_count = admin_service.get_pending_guides_count()
    
    context = {
        'section': 'guides',
        'title': _('Guides'),
        'is_staff': is_staff,
        'pending_guides_count': pending_guides_count,
        'all_parent_guides': all_parent_guides,
        'all_nutrition_guides': all_nutrition_guides,
        'recent_parent_guides': recent_parent_guides,
        'recent_nutrition_guides': recent_nutrition_guides,
        'popular_parent_guides': popular_parent_guides,
        'popular_nutrition_guides': popular_nutrition_guides,
    }
    
    return render(request, 'guides/index.html', context)

def guide_list_view(request, guide_type):
    """Generic view for guide listings"""
    try:
        service = GuideService_Factory.create_service(guide_type)
        if not service:
            messages.error(request, _(f"Invalid guide type: {guide_type}"))
            return redirect('guides')
        
        print(f"guide_type: {guide_type}")
        
        show_all = request.GET.get('show_all') == 'true'
        category_id = request.GET.get('category')
        age_group = request.GET.get('age_group')
        sort_by = request.GET.get('sort', 'newest')
        
        try:
            # Get guides based on filters, handling the approval status properly
            try:
                # Try with only_approved parameter if service supports it
                all_guides = service.get_all_guides(only_approved=True)
            except TypeError:
                # Fallback if the service doesn't support the parameter
                all_guides = service.get_all_guides()
                
                # Check which field is used for approval status
                model_fields = [f.name for f in all_guides.model._meta.get_fields()]
                
                # Filter based on the available fields
                if 'status' in model_fields:
                    # Assuming 'approved' is a valid status value
                    all_guides = all_guides.filter(status='approved')
                elif 'approved_at' in model_fields:
                    # If there's an approved_at timestamp field, non-null means approved
                    all_guides = all_guides.exclude(approved_at__isnull=True)
                
            # Rest of the filtering logic remains the same
            if category_id and hasattr(service, 'filter_by_category'):
                all_guides = service.filter_by_category(all_guides, category_id)
            
            if guide_type == 'nutrition' and age_group and hasattr(service, 'filter_by_age'):
                all_guides = service.filter_by_age(all_guides, age_group)
            
            # Apply sorting
            if sort_by == 'oldest':
                all_guides = all_guides.order_by('created_at')
            elif sort_by == 'popular' and hasattr(service, 'sort_by_popularity'):
                all_guides = service.sort_by_popularity(all_guides)
            else:  # newest by default
                all_guides = all_guides.order_by('-created_at')
                
            # Get categories for filter dropdown
            categories = service.get_categories() if hasattr(service, 'get_categories') else []
                
            # Handle empty results
            if not all_guides:
                all_guides = []
                
            # ELIMINAR PAGINACIÓN - Usar all_guides directamente
            guides = all_guides
                
            # Build context
            context = {
                'guides': guides,
                'categories': categories,
                'section_type': guide_type,
                'guide_type': guide_type,
                'view_type': 'list',
                'show_all': show_all,
                'current_category': category_id,
                'current_age_group': age_group,
                'current_sort': sort_by
            }
            
            # Add query parameters for pagination links - Mantener por compatibilidad
            query_params = ''
            for key, value in request.GET.items():
                if key != 'page':
                    query_params += f'&{key}={value}'
            
            if query_params:
                context['query_params'] = query_params
                
            # Set template path
            template = f'guides/display/{guide_type}_guide_list.html'
            print(f"Using template: {template}")
            
            # Enhance context with additional data
            context = view_helper.enhance_context(context, guide_type, request)
            return render(request, template, context)
        except Exception as e:
            print(f"Error in guide_list_view: {str(e)}")
            messages.error(request, str(e))
            return redirect('guides')
    except ValueError as e:
        messages.error(request, str(e))
        return redirect('guides')
           

def guide_detail_view(request, pk, guide_type=None):
    """View for displaying a specific guide's details"""
    try:
        service = GuideService_Factory.create_service(guide_type)
        guide = service.get_guide_detail(pk)
        
        if not guide:
            messages.error(request, _("The requested guide was not found."))
            return redirect('guides')
        
        if request.method == 'POST' and 'comment_action' in request.POST:
            if request.user.is_authenticated:
                content = request.POST.get('content', '').strip()
                if content:
                    comment_service = Comment_Service()
                    comment_service.add_comment(
                        content_type_str=f"{guide_type}_guide",  # Note the format needed by the method
                        object_id=pk,
                        content=content,
                        user=request.user
                    )
                    messages.success(request, _("Your comment has been posted."))
            return redirect(request.path)
        
        related_guides = service.get_related_guides(guide.id)
        context = {
            'guide': guide,
            'related_guides': related_guides,
            'view_type': 'detail',
            'section': 'guides'
        }
        
        context = view_helper.enhance_context(context, guide_type, request)
        template = view_helper.get_template(guide_type, 'detail')
        return render(request, template, context)
    except ValueError as e:
        messages.error(request, str(e))
        return redirect('guides')

def admin_guides_panel_view(request):
    """Unified admin panel showing guides by type and review status"""
    try:
        if not request.user.is_authenticated:
            messages.warning(request, _("You must be logged in to view your guides"))
            return redirect('login')
        
        # Initialize services
        parent_service = GuideService_Factory.create_service('parent')
        nutrition_service = GuideService_Factory.create_service('nutrition')
        admin_service = AdminGuide_Service()
        
        # Prepare data structure for the panel
        guides_data = {
            'parent': {
                'approved': [],
                'pending': [],
                'total_approved': 0,
                'total_pending': 0
            },
            'nutrition': {
                'approved': [],
                'pending': [],
                'total_approved': 0,
                'total_pending': 0
            }
        }
        
        # Get user's own guides if not staff (optional, can be removed if not needed)
        user_guides = []
        if request.user.is_authenticated and not request.user.is_staff:
            parent_guides = parent_service.get_user_guides(request.user)
            nutrition_guides = nutrition_service.get_user_guides(request.user)
            user_guides = list(parent_guides) + list(nutrition_guides)
            user_guides.sort(key=lambda x: x.created_at, reverse=True)
        
        # For staff users, populate the guides data structure
        if request.user.is_staff:
            # Get all parent guides and categorize them
            all_parent_guides = parent_service.get_all_guides()
            guides_data['parent']['approved'] = [g for g in all_parent_guides if g.is_approved]
            guides_data['parent']['pending'] = [g for g in all_parent_guides if not g.is_approved]
            guides_data['parent']['total_approved'] = len(guides_data['parent']['approved'])
            guides_data['parent']['total_pending'] = len(guides_data['parent']['pending'])
            
            # Get all nutrition guides and categorize them
            all_nutrition_guides = nutrition_service.get_all_guides()
            guides_data['nutrition']['approved'] = [g for g in all_nutrition_guides if g.is_approved]
            guides_data['nutrition']['pending'] = [g for g in all_nutrition_guides if not g.is_approved]
            guides_data['nutrition']['total_approved'] = len(guides_data['nutrition']['approved'])
            guides_data['nutrition']['total_pending'] = len(guides_data['nutrition']['pending'])
            
            # Calculate total counts
            total_approved = guides_data['parent']['total_approved'] + guides_data['nutrition']['total_approved']
            total_pending = guides_data['parent']['total_pending'] + guides_data['nutrition']['total_pending']
            total_guides = total_approved + total_pending
        
        context = {
            'guides_data': guides_data,
            'user_guides': user_guides,
            'title': _('Guides Administration'),
            'section': 'guides',
            'section_type': 'admin_guides_panel',
            'is_staff': request.user.is_staff,
            'total_stats': {
                'approved': total_approved,
                'pending': total_pending,
                'total': total_guides
            }
        }
        
        return render(request, 'guides/admin/admin_guides_panel.html', context)
    except ValueError as e:
        messages.error(request, str(e))
        return redirect('guides')