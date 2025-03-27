# Views Directory Structure 

```
views/
├── __init__.py                # Main imports and exports
├── README.md                  # Documentation
├── base/                      # Base view components
│   ├── __init__.py
│   ├── base_views.py          # Common base classes
│   ├── error_views.py         # Error handling views
│   └── home_views.py          # Home and general pages
├── auth/                      # Authentication views
│   ├── __init__.py
│   └── auth_views.py          # Login, Logout, Register, Profile
├── child/                     # Child management
│   ├── __init__.py
│   ├── core_views.py          # Main child views
│   ├── feature_views.py       # Calendar, Vaccines, Milestones
│   └── form_views.py          # Add/Edit/Delete child forms
├── guides/                    # Guide-related views
│   ├── __init__.py
│   ├── guide_views.py         # Guide management
│   ├── article_views.py       # External articles
│   └── submission_views.py    # Guide submission
├── nutrition/                 # Nutrition-specific views
│   ├── __init__.py
│   ├── analyzer_views.py      # Nutrition analyzer
│   └── comparison_views.py    # Nutrition comparison
├── forum/                     # Forum functionality
│   ├── __init__.py
│   └── forum_views.py         # Forum views
├── admin/                     # Admin functionality
│   ├── __init__.py
│   └── admin_views.py         # Administrative functions
├── comments/                  # Comment functionality
│   ├── __init__.py
│   └── comment_views.py       # Comment views          
└── contact/                   # Contact functionality
    ├── __init__.py
    └── contact_views.py       # Contact form
```