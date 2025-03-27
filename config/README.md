# Config Directory Structure 

```
config/
├── __init__.py
├── settings/                # Split settings
│   ├── __init__.py
│   ├── base.py
│   ├── development.py
│   ├── production.py
│   └── testing.py
└── asgi.py                  # ASGI configuration
```