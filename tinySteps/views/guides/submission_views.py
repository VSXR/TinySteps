import os
import logging
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils.translation import gettext as _
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.middleware.csrf import get_token

from tinySteps.forms import GuideSubmission_Form
from tinySteps.factories import GuideService_Factory

logger = logging.getLogger(__name__)

class SubmitGuide_View(LoginRequiredMixin, View):
    """Guide submission view"""
    
    def get(self, request, guide_type=None):
        """Handle GET request - show form"""
        guide_type = guide_type or request.GET.get('type', 'parent')
        
        valid_types = ['parent', 'nutrition']
        if guide_type not in valid_types:
            guide_type = 'parent'
            
        form = GuideSubmission_Form(guide_type=guide_type)
        tag_categories = form.get_tag_categories(guide_type)
        
        # Add a unique submission token to the session
        if 'guide_submit_token' not in request.session:
            request.session['guide_submit_token'] = get_token(request)
        
        return render(request, 'guides/submit.html', {
            'form': form,
            'guide_type': guide_type,
            'title': _("Submit Guide"),
            'tag_categories': tag_categories,
            'section_type': guide_type,
            'submit_token': request.session['guide_submit_token']  # Pass token to template
        })
    
    def post(self, request, guide_type=None):
        """Handle POST request - process form"""
        # Check if this is a duplicate submission
        submitted_token = request.POST.get('submit_token')
        stored_token = request.session.get('guide_submit_token')
        
        if not submitted_token or submitted_token != stored_token:
            messages.error(request, _("Your form may have been submitted twice. Please try again."))
            return redirect('submit_guide')
        
        guide_type = guide_type or request.POST.get('guide_type', 'parent')
        
        valid_types = ['parent', 'nutrition']
        if guide_type not in valid_types:
            guide_type = 'parent'
        
        form = GuideSubmission_Form(request.POST, request.FILES, guide_type=guide_type)
        if form.is_valid():
            # Generate a new token to prevent resubmission
            request.session['guide_submit_token'] = get_token(request)
            
            try:
                service = GuideService_Factory.create_service(guide_type)
                
                # If no image was provided, use default
                if not form.cleaned_data.get('image'):
                    try:
                        self._apply_default_image(form, guide_type, request)
                    except Exception as e:
                        logger.error(f"Error applying default image: {str(e)}")
                        messages.warning(request, _("There was an issue with the default image. Your guide will be submitted without an image."))
                
                # Create guide with 'pending' status
                guide_instance = form.save(commit=False)
                guide_instance.author = request.user
                guide_instance.guide_type = guide_type
                guide_instance.status = 'pending'  # Ensure status is pending
                guide_instance.save()
                
                # Handle tags
                tags = form.cleaned_data.get('tags', '')
                if tags and hasattr(guide_instance, 'tags'):
                    guide_instance.set_tags(tags)
                
                messages.success(request, 
                    _("Your guide has been submitted for review. You'll be notified when it's approved."))
                
                # Redirect based on user role
                if request.user.is_staff or request.user.is_superuser:
                    # Admins and staff go to the guide review panel
                    return redirect('admin_guides_panel')
                else:
                    # Regular users go to the guide listing page
                    return redirect('guides')
                    
            except Exception as e:
                logger.error(f"Error creating guide: {str(e)}")
                messages.error(request, _("There was an error submitting your guide."))
        else:
            logger.warning(f"Invalid form submission: {form.errors}")
        
        # If form is invalid, generate a new token for the form
        request.session['guide_submit_token'] = get_token(request)
        
        tag_categories = form.get_tag_categories(guide_type)
        return render(request, 'guides/submit.html', {
            'form': form,
            'guide_type': guide_type,
            'title': _("Submit Guide"),
            'tag_categories': tag_categories,
            'section_type': guide_type,
            'submit_token': request.session['guide_submit_token']  # Pass token to template
        })
    
    def _apply_default_image(self, form, guide_type, request):
        """Apply default image based on guide type"""
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        if guide_type == 'nutrition':
            default_img_path = os.path.join(base_dir, 'static', 'res', 'img', 'others', 'nutrition_guide.jpg')
        else:
            default_img_path = os.path.join(base_dir, 'static', 'res', 'img', 'others', 'parent_guide.jpg')
        
        if os.path.exists(default_img_path):
            with open(default_img_path, 'rb') as f:
                data = f.read()
            filename = os.path.basename(default_img_path)
            form.files['image'] = ContentFile(data, name=filename)
        else:
            messages.warning(request, _("Default image not found. Your guide will be submitted without an image."))