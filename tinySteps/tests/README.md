# Tests Directory Structure 

```
tinySteps/
├── tests/
│   ├── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── test_child_models.py
│   │   ├── test_content_models.py
│   │   └── test_forum_models.py
│   ├── views/
│   │   ├── __init__.py
│   │   ├── test_auth_views.py
│   │   ├── test_child_views.py
│   │   ├── test_forum_views.py
│   │   └── test_guide_views.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── test_nutrition_service.py
│   │   ├── test_edamam_service.py
│   │   └── test_forum_service.py
│   ├── forms/
│   │   ├── __init__.py
│   │   ├── test_child_forms.py
│   │   └── test_guide_forms.py
│   ├── api/
│   │   ├── __init__.py
│   │   └── test_vaccine_api.py
│   └── functional/
│       ├── __init__.py
│       ├── test_vaccine_workflow.py
│       └── test_guide_workflow.py
```