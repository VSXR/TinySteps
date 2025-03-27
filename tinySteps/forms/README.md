# Forms Directory Structure 

```
forms/
├── __init__.py                    # Main imports and exports
├── README.md                      # Documentation
├── base/                          # Base form classes and mixins
│   ├── __init__.py
│   └── mixins.py                  # Form field mixins for reusability
├── auth/                          # Authentication forms
│   ├── __init__.py
│   └── auth_forms.py              # Registration and password forms
├── child/                         # Child-related forms
│   ├── __init__.py
│   ├── core_forms.py              # Basic child information
│   └── feature_forms.py           # Calendar, vaccines, milestones
├── communication/                 # Communication forms
│   ├── __init__.py
│   ├── contact_forms.py           # Contact forms
│   └── comment_forms.py           # Comment forms
└── content/                       # Content creation forms
    ├── __init__.py
    ├── guide_forms.py             # Guide submission/moderation
    └── forum_forms.py             # Forum post creation
```