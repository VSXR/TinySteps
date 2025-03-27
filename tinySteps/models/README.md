# Models Directory Structure 

```
models/
├── __init__.py                 # Main imports and exports
├── README.md                   # Documentation
├── base/                       # Base models and mixins
│   ├── __init__.py
│   └── mixins.py               # CommentableMixin, LikeableMixin
├── user/                       # User-related models
│   ├── __init__.py
│   └── user_models.py          # Profile_Model, PasswordReset_Model
├── child/                      # Child-related models
│   ├── __init__.py
│   └── child_models.py         # YourChild_Model, Milestone_Model, etc.
├── content/                    # Content models
│   ├── __init__.py
│   ├── comment_models.py       # Comment_Model, Like_Model
│   ├── guide_models.py         # Guide_Interface, Guides_Model, etc.
│   └── forum_models.py         # ParentsForum_Model
├── communication/              # Communication models
│   ├── __init__.py
│   ├── notification_models.py  # Notification_Model
│   └── contact_models.py       # Contact_Model
└── external/                   # External API models
    ├── __init__.py
    ├── article_models.py       # ExternalArticle_Model
    └── nutrition_models.py     # ExternalNutritionData_Model
```