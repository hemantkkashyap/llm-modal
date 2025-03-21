INSTALLED_APPS = [
    # Other apps
    'corsheaders',
]

MIDDLEWARE = [
    # Other middleware
    'corsheaders.middleware.CorsMiddleware',
]

# Allow all origins
CORS_ALLOW_ALL_ORIGINS = True
