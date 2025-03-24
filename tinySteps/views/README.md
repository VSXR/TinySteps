TinySteps/
├── tinySteps/                        # Main application folder
│   ├── __init__.py
│   ├── admin.py                      # Django admin configuration
│   ├── apps.py                       # App configuration
│   ├── forms.py                      # Form definitions
│   ├── helpers.py                    # Helper functions
│   ├── middleware.py                 # Custom middleware
│   ├── models.py                     # Database models
│   ├── registry.py                   # Registry for guide types
│   ├── repositories.py               # Data access layer
│   ├── urls.py                       # URL routing
│   ├── utils.py                      # Utility functions
│   ├── factories.py                  # Factory classes
│   │
│   ├── views/                        # Views directory (split by functionality)
│   │   ├── __init__.py               # Imports and exposes all views
│   │   ├── admin_views.py            # Admin-related views
│   │   ├── auth_views.py             # Authentication views
│   │   ├── base_views.py             # Base classes for views
│   │   ├── child_views.py            # Child management views
│   │   ├── error_views.py            # Error handling views
│   │   ├── forum_views.py            # Forum-related views
│   │   ├── guide_views.py            # Guide-related views
│   │   ├── home_views.py             # Homepage and index views
│   │   └── nutrition_views.py        # Nutrition-specific views
│   │
│   ├── services/                     # Services directory (business logic)
│   │   ├── __init__.py               # Imports and exposes all services
│   │   ├── admin_service.py          # Admin operations
│   │   ├── article_service.py        # Article operations
│   │   ├── edamam_service.py         # Edamam API integration
│   │   ├── guide_service.py          # Base guide service
│   │   ├── guide_context_service.py  # Context data for guides
│   │   ├── nutrition_data_service.py # Nutrition data operations
│   │   ├── nutrition_guide_service.py # Nutrition guide operations
│   │   └── parent_guide_service.py   # Parent guide operations
│   │
│   └── templates/                    # Template files
│       └── ...
│
├── manage.py                         # Django management script
└── ...