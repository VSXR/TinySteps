# Repositories Directory Structure 

```
repositories/
├── __init__.py                # Main imports
├── base/                      # Base repository interfaces
│   ├── __init__.py
│   └── base_repository.py     # Generic repository interfaces
├── child/                     # Child repositories
│   ├── __init__.py
│   └── child_repository.py
├── content/                   # Content repositories
│   ├── __init__.py
│   ├── guide_repository.py
│   ├── article_repository.py
│   └── forum_repository.py
├── user/                      # User repositories
│   ├── __init__.py
│   └── user_repository.py
└── nutrition/                 # Nutrition repositories
    ├── __init__.py
    └── nutrition_repository.py
```