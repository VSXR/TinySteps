from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils.translation import gettext as _
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin

from tinySteps.forms import GuideSubmission_Form
from tinySteps.factories import GuideService_Factory

class SubmitGuide_View(LoginRequiredMixin, View):
    """Guide submission view"""
    
    def get(self, request, guide_type=None):
        """Handle GET request - show form"""
        if not guide_type:
            guide_type = 'parent'
        
        form = GuideSubmission_Form()
        return render(request, 'guides/submit.html', {
            'form': form,
            'guide_type': guide_type
        })
    
    def post(self, request, guide_type=None):
        """Handle POST request - process form"""
        if not guide_type:
            guide_type = 'parent'
        
        form = GuideSubmission_Form(request.POST, request.FILES)
        if form.is_valid():
            service = GuideService_Factory.create_service(guide_type)
            created_guide = service.create_guide_from_form(form, request.user)
            messages.success(request, _("Your guide has been submitted for review!"))
            return redirect('my_guides')
        
        return render(request, 'guides/submit.html', {
            'form': form,
            'guide_type': guide_type
        })

@login_required
def submit_guide(request):
    """Get the guide type from the request and handle the submission
    The default guide type is parent!
    """
    guide_type = request.GET.get('type', 'parent')
    
    valid_types = ['parent', 'nutrition']
    if guide_type not in valid_types:
        guide_type = 'parent'  # Default to parent if invalid
    
    if request.method == 'POST':
        form = GuideSubmission_Form(request.POST, request.FILES)
        if form.is_valid():
            guide = form.save(commit=False)
            guide.author = request.user
            guide.guide_type = request.POST.get('guide_type', guide_type)
            guide.status = 'pending'
            guide.save()
            
            tags = form.cleaned_data.get('tags', '')
            if tags:
                guide.tags = tags.strip()
                guide.save()
            
            messages.success(request, 
                _("Your guide has been submitted for review. Thank you for contributing!"))
            return redirect('my_guides')
    else:
        form = GuideSubmission_Form()
    
    # Get tag categories for the selected guide type
    tag_categories = form.get_tag_categories(guide_type)
    
    context = {
        'form': form,
        'guide_type': guide_type,
        'title': _("Submit Guide"),
        'tag_categories': tag_categories
    }
    
    return render(request, 'guides/submit.html', context)