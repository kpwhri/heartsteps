import os, environ

env = environ.Env()

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

root = environ.Path(BASE_DIR)
SITE_ROOT = root()

STATIC_ROOT = root('static')
STATIC_URL = '/static/'

SECRET_KEY = env('SECRET_KEY', default='secret-key')
DEBUG = env.bool('DEBUG', default=False)

# Fitbit settings
FITAPP_CONSUMER_KEY = env('FITAPP_CONSUMER_KEY', default='CONSUMER_KEY')
FITAPP_CONSUMER_SECRET = env('FITAPP_CONSUMER_SECRET', default='CONSUMER_SECRET')
FITAPP_SUBSCRIBE = env.bool('FITAPP_SUBSCRIBE', default=False)
FITAPP_SUBSCRIBER_ID = env('FITAPP_SUBSCRIBER_ID', default='SUBSCRIBER_ID')
FITAPP_VERIFICATION_CODE = env('FITAPP_VERIFICATION_CODE', default='VERIFICATION_CODE')

ALLOWED_HOSTS = env.str('HOST_NAME', default='localhost,127.0.0.1,server').split(',')

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_celery_results',
    'django_celery_beat',
    'rest_framework',
    'rest_framework.authtoken',
    'contact',
    'fitapp',
    'fitbit_api',
    'behavioral_messages',
    'morning_messages',
    'push_messages',
    'weekly_reflection',
    'participants',
    'locations',
    'weather',
    'randomization',
    'activity_suggestions',
    'activity_logs',
    'activity_plans'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
    )
}

FCM_SERVER_KEY = env('FCM_SERVER_KEY', default='secret-key')

CELERY_BROKER_URL = 'amqp://guest:guest@localhost:5672//'
CELERY_RESULT_BACKEND = 'django-db'
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'

FIXTURE_DIRS = [
    root('fixtures')
]

ROOT_URLCONF = 'heartsteps.urls'

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

WSGI_APPLICATION = 'heartsteps.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': env.db(),
}

# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

HEARTSTEPS_LOCATIONS_NEAR_DISTANCE = env.float('HEARTSTEPS_LOCATIONS_NEAR_DISTANCE', default=0.25)
