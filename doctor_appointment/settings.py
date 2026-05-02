from pathlib import Path
from datetime import timedelta
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY', default='django-insecure-change-this-in-production')
DEBUG = config('DEBUG', default=True, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1').split(',')

INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third party
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'django_filters',
    'drf_spectacular',
    
    # Local apps
    'users',
    'doctors',
    'appointments',
    'payments',
    'notifications',
    'reviews',
    'faqs',
    'settings_app',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'doctor_appointment.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'doctor_appointment.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME', default='Doctorapp_db'),
        'USER': config('DB_USER', default='postgres'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5050'),
        # Performance optimizations
        'CONN_MAX_AGE': 600,  # Keep connections alive for 10 minutes
        'OPTIONS': {
            'connect_timeout': 10,
            'options': '-c statement_timeout=30000'  # 30 second query timeout
        },
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'  # Directory where collectstatic will collect static files
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
AUTH_USER_MODEL = 'users.User'

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    # Performance: Enable compression
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
    # Security: Rate limiting (requires django-ratelimit or throttling)
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',  # Anonymous users: 100 requests per hour
        'user': '1000/hour'  # Authenticated users: 1000 requests per hour
    }
}

# drf-spectacular settings
SPECTACULAR_SETTINGS = {
    'TITLE': 'MediBook Doctor Appointment API',
    'DESCRIPTION': 'Comprehensive REST API for doctor appointment booking system with patient management, doctor profiles, appointments, prescriptions, payments, reviews, and notifications.',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    
    # Authentication
    'SECURITY': [{'bearerAuth': []}],
    'COMPONENT_SPLIT_REQUEST': True,
    
    # Schema generation
    'SCHEMA_PATH_PREFIX': '/api/',
    'SCHEMA_PATH_PREFIX_TRIM': True,
    'CAMELIZE_NAMES': False,
    
    # UI customization
    'SWAGGER_UI_SETTINGS': {
        'deepLinking': True,
        'persistAuthorization': True,
        'displayOperationId': True,
        'filter': True,
        'defaultModelsExpandDepth': 2,
        'defaultModelExpandDepth': 2,
        'docExpansion': 'list',
        'displayRequestDuration': True,
    },
    
    'REDOC_UI_SETTINGS': {
        'hideDownloadButton': False,
        'expandResponses': '200,201',
        'pathInMiddlePanel': True,
    },
    
    # Tags for grouping
    'TAGS': [
        {'name': 'Authentication', 'description': 'User registration, login, and profile management'},
        {'name': 'Doctors', 'description': 'Doctor profiles, availability, and search'},
        {'name': 'Appointments', 'description': 'Appointment booking, management, and prescriptions'},
        {'name': 'Payments', 'description': 'Payment processing and history'},
        {'name': 'Reviews', 'description': 'Doctor reviews and ratings'},
        {'name': 'Notifications', 'description': 'User notifications'},
        {'name': 'Admin', 'description': 'Administrative operations'},
    ],
    
    # Security schemes
    'APPEND_COMPONENTS': {
        'securitySchemes': {
            'bearerAuth': {
                'type': 'http',
                'scheme': 'bearer',
                'bearerFormat': 'JWT',
                'description': 'JWT token obtained from /api/auth/login/ endpoint. Format: Bearer {token}',
            }
        }
    },
    
    # Component naming
    'COMPONENT_NO_READ_ONLY_REQUIRED': True,
    'SORT_OPERATIONS': True,
}

# JWT Settings
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
    # Security enhancements
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
}

# CORS Settings
CORS_ALLOWED_ORIGINS = config('CORS_ALLOWED_ORIGINS', default='http://localhost:3000').split(',')
CORS_ALLOW_CREDENTIALS = True

# ── Jazzmin Admin Theme ──
JAZZMIN_SETTINGS = {
    "site_title": "MediBook Admin",
    "site_header": "MediBook",
    "site_brand": "MediBook",
    "site_logo": None,
    "login_logo": None,
    "site_icon": None,
    "welcome_sign": "Welcome to MediBook Administration",
    "copyright": "MediBook Doctor Appointment System",
    "search_model": ["users.User", "doctors.Doctor", "appointments.Appointment"],
    "user_avatar": None,

    # Top menu
    "topmenu_links": [
        {"name": "Home", "url": "admin:index", "permissions": ["auth.view_user"]},
        {"name": "Frontend", "url": "http://localhost:3000", "new_window": True},
        {"model": "users.User"},
    ],

    # Side menu
    "show_sidebar": True,
    "navigation_expanded": True,
    "hide_apps": [],
    "hide_models": [],
    "order_with_respect_to": [
        "users", "doctors", "appointments", "payments", "notifications", "reviews",
    ],

    "icons": {
        "auth": "fas fa-users-cog",
        "users.user": "fas fa-user",
        "doctors.doctor": "fas fa-user-md",
        "doctors.doctoravailability": "fas fa-calendar-check",
        "appointments.appointment": "fas fa-calendar-alt",
        "appointments.prescription": "fas fa-prescription",
        "appointments.medicine": "fas fa-pills",
        "payments.payment": "fas fa-credit-card",
        "notifications.notification": "fas fa-bell",
        "reviews.review": "fas fa-star",
    },
    "default_icon_parents": "fas fa-chevron-circle-right",
    "default_icon_children": "fas fa-circle",

    "related_modal_active": True,
    "custom_css": None,
    "custom_js": None,
    "use_google_fonts_cdn": True,
    "show_ui_builder": False,
    "changeform_format": "horizontal_tabs",
    "changeform_format_overrides": {
        "auth.user": "collapsible",
        "auth.group": "vertical_tabs",
    },
}

JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": "navbar-primary",
    "accent": "accent-primary",
    "navbar": "navbar-dark",
    "no_navbar_border": False,
    "navbar_fixed": True,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": True,
    "sidebar": "sidebar-dark-primary",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": True,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": False,
    "theme": "default",
    "dark_mode_theme": None,
    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success",
    },
}


# ══════════════════════════════════════════════════════════════════════════════
# SECURITY SETTINGS
# ══════════════════════════════════════════════════════════════════════════════

# Security Headers
SECURE_BROWSER_XSS_FILTER = True  # Enable XSS filter
SECURE_CONTENT_TYPE_NOSNIFF = True  # Prevent MIME type sniffing
X_FRAME_OPTIONS = 'DENY'  # Prevent clickjacking
SECURE_REFERRER_POLICY = 'same-origin'  # Control referrer information

# HTTPS Settings (Enable in production)
# SECURE_SSL_REDIRECT = True  # Redirect all HTTP to HTTPS
# SESSION_COOKIE_SECURE = True  # Only send session cookie over HTTPS
# CSRF_COOKIE_SECURE = True  # Only send CSRF cookie over HTTPS
# SECURE_HSTS_SECONDS = 31536000  # Enable HSTS for 1 year
# SECURE_HSTS_INCLUDE_SUBDOMAINS = True
# SECURE_HSTS_PRELOAD = True

# Session Security
SESSION_COOKIE_HTTPONLY = True  # Prevent JavaScript access to session cookie
SESSION_COOKIE_SAMESITE = 'Lax'  # CSRF protection
SESSION_COOKIE_AGE = 86400  # Session expires after 24 hours
SESSION_SAVE_EVERY_REQUEST = False  # Don't save session on every request (performance)
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

# CSRF Security
CSRF_COOKIE_HTTPONLY = True  # Prevent JavaScript access to CSRF cookie
CSRF_COOKIE_SAMESITE = 'Lax'
CSRF_USE_SESSIONS = False
CSRF_COOKIE_AGE = 31449600  # 1 year

# Password Security (already configured but adding comments)
# - UserAttributeSimilarityValidator: Password can't be too similar to user info
# - MinimumLengthValidator: Minimum 8 characters
# - CommonPasswordValidator: Prevents common passwords
# - NumericPasswordValidator: Password can't be entirely numeric

# Content Security Policy (CSP)
# Add django-csp package for full CSP support
# CSP_DEFAULT_SRC = ("'self'",)
# CSP_SCRIPT_SRC = ("'self'", "'unsafe-inline'")
# CSP_STYLE_SRC = ("'self'", "'unsafe-inline'")
# CSP_IMG_SRC = ("'self'", "data:", "https:")
# CSP_FONT_SRC = ("'self'", "data:")

# ══════════════════════════════════════════════════════════════════════════════
# PERFORMANCE SETTINGS
# ══════════════════════════════════════════════════════════════════════════════

# Database Query Optimization
# Log slow queries in development
if DEBUG:
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
            },
        },
        'loggers': {
            'django.db.backends': {
                'handlers': ['console'],
                'level': 'DEBUG' if config('LOG_SQL', default=False, cast=bool) else 'INFO',
            },
        },
    }

# Caching Configuration (using local memory cache for development)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
        'TIMEOUT': 300,  # 5 minutes default timeout
        'OPTIONS': {
            'MAX_ENTRIES': 1000
        }
    }
}

# For production, use Redis:
# CACHES = {
#     'default': {
#         'BACKEND': 'django_redis.cache.RedisCache',
#         'LOCATION': 'redis://127.0.0.1:6379/1',
#         'OPTIONS': {
#             'CLIENT_CLASS': 'django_redis.client.DefaultClient',
#             'CONNECTION_POOL_KWARGS': {'max_connections': 50}
#         }
#     }
# }

# Static Files Optimization
# Using StaticFilesStorage instead of ManifestStaticFilesStorage to avoid issues with missing source maps
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# File Upload Settings
FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
FILE_UPLOAD_PERMISSIONS = 0o644

# ══════════════════════════════════════════════════════════════════════════════
# ADDITIONAL SECURITY MEASURES
# ══════════════════════════════════════════════════════════════════════════════

# Prevent host header attacks
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1').split(',')

# Admin Security
ADMIN_URL = config('ADMIN_URL', default='admin/')  # Can be changed to hide admin panel

# Email Security (for password reset, notifications, etc.)
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
# EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
# EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
# DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='noreply@medibook.com')

# Security Middleware Order (already configured but documenting)
# 1. SecurityMiddleware - Adds security headers
# 2. CorsMiddleware - Handles CORS
# 3. SessionMiddleware - Manages sessions
# 4. CommonMiddleware - Common operations
# 5. CsrfViewMiddleware - CSRF protection
# 6. AuthenticationMiddleware - User authentication
# 7. MessageMiddleware - Flash messages
# 8. ClickjackingMiddleware - Clickjacking protection

# ══════════════════════════════════════════════════════════════════════════════
# MONITORING & LOGGING (Production)
# ══════════════════════════════════════════════════════════════════════════════

# For production, add proper logging:
# LOGGING = {
#     'version': 1,
#     'disable_existing_loggers': False,
#     'formatters': {
#         'verbose': {
#             'format': '{levelname} {asctime} {module} {message}',
#             'style': '{',
#         },
#     },
#     'handlers': {
#         'file': {
#             'level': 'WARNING',
#             'class': 'logging.handlers.RotatingFileHandler',
#             'filename': BASE_DIR / 'logs' / 'django.log',
#             'maxBytes': 1024 * 1024 * 15,  # 15MB
#             'backupCount': 10,
#             'formatter': 'verbose',
#         },
#         'security_file': {
#             'level': 'WARNING',
#             'class': 'logging.handlers.RotatingFileHandler',
#             'filename': BASE_DIR / 'logs' / 'security.log',
#             'maxBytes': 1024 * 1024 * 15,
#             'backupCount': 10,
#             'formatter': 'verbose',
#         },
#     },
#     'loggers': {
#         'django': {
#             'handlers': ['file'],
#             'level': 'WARNING',
#             'propagate': True,
#         },
#         'django.security': {
#             'handlers': ['security_file'],
#             'level': 'WARNING',
#             'propagate': False,
#         },
#     },
# }
