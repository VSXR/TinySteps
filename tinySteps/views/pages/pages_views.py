from django.shortcuts import render
from django.utils.translation import gettext as _

def terms_view(request):
    """Terms and Conditions page view"""
    policy_links = [
        {'id': 'introduction', 'title': _('Introduction'), 'number': '1'},
        {'id': 'account', 'title': _('Your Account'), 'number': '2'},
        {'id': 'content', 'title': _('User Content'), 'number': '3'},
        {'id': 'privacy', 'title': _('Privacy'), 'number': '4'},
        {'id': 'intellectual', 'title': _('Intellectual Property'), 'number': '5'},
        {'id': 'termination', 'title': _('Termination'), 'number': '6'},
        {'id': 'disclaimer', 'title': _('Disclaimer'), 'number': '7'},
        {'id': 'liability', 'title': _('Limitation of Liability'), 'number': '8'},
        {'id': 'changes', 'title': _('Changes'), 'number': '9'},
        {'id': 'contact', 'title': _('Contact Us'), 'number': '10'},
    ]
    return render(request, 'pages/policies/terms.html', {'policy_links': policy_links})

def privacy_view(request):
    """Privacy Policy page view"""
    policy_links = [
        {'id': 'introduction', 'title': _('Introduction'), 'number': '1'},
        {'id': 'data-collection', 'title': _('Data Collection'), 'number': '2'},
        {'id': 'data-use', 'title': _('Use of Data'), 'number': '3'},
        {'id': 'data-sharing', 'title': _('Data Sharing'), 'number': '4'},
        {'id': 'data-retention', 'title': _('Data Retention'), 'number': '5'},
        {'id': 'your-rights', 'title': _('Your Rights'), 'number': '6'},
        {'id': 'security', 'title': _('Security'), 'number': '7'},
        {'id': 'changes', 'title': _('Changes to Policy'), 'number': '8'},
        {'id': 'contact', 'title': _('Contact Us'), 'number': '9'},
    ]
    return render(request, 'pages/policies/privacy.html', {'policy_links': policy_links})

def cookies_view(request):
    """Cookie Policy page view"""
    policy_links = [
        {'id': 'introduction', 'title': _('Introduction'), 'number': '1'},
        {'id': 'what-are-cookies', 'title': _('What Are Cookies'), 'number': '2'},
        {'id': 'how-we-use', 'title': _('How We Use Cookies'), 'number': '3'},
        {'id': 'managing-cookies', 'title': _('Managing Cookies'), 'number': '4'},
        {'id': 'third-party', 'title': _('Third Party Cookies'), 'number': '5'},
        {'id': 'more-info', 'title': _('More Information'), 'number': '6'},
        {'id': 'contact', 'title': _('Contact Us'), 'number': '7'},
    ]
    return render(request, 'pages/policies/cookies.html', {'policy_links': policy_links})

def accessibility_view(request):
    """Accessibility Statement page view"""
    policy_links = [
        {'id': 'our-commitment', 'title': _('Our Commitment to Accessibility')},
        {'id': 'conformance-status', 'title': _('Conformance Status')},
        {'id': 'accessibility-features', 'title': _('Accessibility Features')},
        {'id': 'feedback', 'title': _('Feedback')},
    ]
    return render(request, 'pages/policies/accessibility.html', {'policy_links': policy_links})

def help_center_view(request):
    """Help Center page view"""
    return render(request, 'pages/policies/help_center.html')