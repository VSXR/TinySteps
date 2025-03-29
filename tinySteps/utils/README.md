# Utils Directory Structure 

```
utils/
├── __init__.py                # Main exports
├── README.md                  # Documentation
├── decorators/
│   ├── __init__.py
│   ├── caching.py             # Result caching decorators
│   └── permissions.py         # Access control decorators
├── helpers/
│   ├── __init__.py
│   ├── guides_helper.py       # Guide-specific helpers
│   ├── helpers.py             # General helpers (backward compatibility)
│   └── view_helpers.py        # View-related helpers with implementations
├── interfaces/
│   ├── __init__.py
│   └── view_interfaces.py     # Interface definitions for view helpers
└── middleware/
    ├── __init__.py
    ├── error_handling.py      # Error handling middleware
    └── request_logging.py     # Request logging middleware
```