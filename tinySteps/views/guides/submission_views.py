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
def submit_guide(request, guide_type=None):
    """Function-based view wrapper for SubmitGuide_View"""
    view = SubmitGuide_View.as_view()
    return view(request, guide_type=guide_type)