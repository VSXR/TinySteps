# Utils Directory Structure 

```
utils/
├── __init__.py                # Main imports and exports
├── README.md                  # This file
├── decorators/                # Function decorators
│   ├── __init__.py            # Decorator exports
│   ├── caching.py             # Result caching decorators
│   └── permissions.py         # Access control decorators
├── helpers/                   # Utility functions
│   ├── __init__.py            # Helper exports
│   ├── events.py              # Event-related utilities
│   ├── formatting.py          # Text formatting utilities
│   ├── validation.py          # Data validation utilities
│   └── views.py               # View-related helpers
└── middleware/                # Request processing middleware
    ├── __init__.py            # Middleware exports
    ├── error_handling.py      # Error handling middleware
    └── request_logging.py     # Request logging middleware

```