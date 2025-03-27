# Services Directory Structure

```
services/
├── __init__.py                  # Main imports
├── core/                        # Core application services
│   ├── __init__.py
│   ├── admin_service.py         # Admin functionality
│   ├── child_service.py         # Child management 
│   └── forum_service.py         # Forum functionality
├── communication/               # Communication services
│   ├── __init__.py
│   └── contact_service.py       # Contact functionality
├── guides/                      # Guide-related services
│   ├── __init__.py
│   ├── base_service.py          # Base guide service 
│   ├── context_service.py       # Guide context functionality
│   ├── nutrition_service.py     # Nutrition-specific guide services
│   └── parent_service.py        # Parent-specific guide services
├── external/                    # External data services
│   ├── __init__.py
│   ├── article_service.py       # Article management
│   └── nutrition_data_service.py # Nutrition data functionality
└── apis/                        # External API integrations
    ├── __init__.py
    ├── currents_service.py      # Currents API integration
    ├── edamam_service.py        # Edamam API integration
    └── news_service.py          # News API integration
```