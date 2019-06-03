import os, environ
from corsheaders.defaults import default_headers

env = environ.Env()

env_file_path = '/server/.env'
if os.path.isfile(env_file_path):
    env.read_env(env_file_path)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
root = environ.Path(BASE_DIR)
SITE_ROOT = root()

STATIC_ROOT = root('static')
STATIC_URL = '/static/'

SECRET_KEY = env.str('SECRET_KEY', default='secret-key')
DEBUG = env.bool('DEBUG', default=False)

ALLOWED_HOSTS = env.str('ALLOWED_HOSTS', default='localhost,127.0.0.1').split(',')

PARTICIPANT_NIGHTLY_UPDATE_TIME = env.str('PARTICIPANT_NIGHTLY_UPDATE', default="1:30")
RANDOMIZATION_FIXED_PROBABILITY = env.float('RANDOMIZATION_FIXED_PROBABILITY', default=0.5)
HEARTSTEPS_LOCATIONS_NEAR_DISTANCE = env.float('HEARTSTEPS_LOCATIONS_NEAR_DISTANCE', default=0.25)

if 'ANTI_SEDENTARY_SERVICE_URL' in os.environ:
    ANTI_SEDENTARY_SERVICE_URL = env('ANTI_SEDENTARY_SERVICE_URL')
ANTI_SEDENTARY_DECISION_MINUTE_INTERVAL = env.int('ANTI_SEDENTARY_DECISION_MINUTE_INTERVAL', default=5)

if 'WALKING_SUGGESTION_SERVICE_URL' in os.environ:
    WALKING_SUGGESTION_SERVICE_URL = env('WALKING_SUGGESTION_SERVICE_URL')
WALKING_SUGGESTION_INITIALIZATION_DAYS = env.int('WALKING_SUGGESTION_INITIALIZATION_DAYS', default=7)
WALKING_SUGGESTION_DECISION_WINDOW_MINUTES = env.int('WALKING_SUGGESTION_DECISION_WINDOW_MINUTES', default=20)
WALKING_SUGGESTION_DECISION_UNAVAILABLE_STEP_COUNT = env.int('WALKING_SUGGESTION_DECISION_UNAVAILABLE_STEP_COUNT', 250)

# Fitbit Settings
FITBIT_CONSUMER_KEY = env.str('FITBIT_CONSUMER_KEY', default='CONSUMER_KEY')
FITBIT_CONSUMER_SECRET = env.str('FITBIT_CONSUMER_SECRET', default='CONSUMER_SECRET')
FITBIT_SUBSCRIBER_ID = env.str('FITBIT_SUBSCRIBER_ID', default='SUBSCRIBER_ID')
FITBIT_SUBSCRIBER_VERIFICATION_CODE = env.str('FITBIT_SUBSCRIBER_VERIFICATION_CODE', default='VERIFICATION_CODE')

FITBIT_ACTIVITY_DAY_MINIMUM_WEAR_DURATION_MINUTES = env.int('FITBIT_ACTIVITY_DAY_MINIMUM_WEAR_DURATION_MINUTES', default=240)

#ONESIGNAL Settings
if 'ONESIGNAL_API_KEY' in os.environ:
    ONESIGNAL_API_KEY = env.str('ONESIGNAL_API_KEY')
if 'ONESIGNAL_APP_ID' in os.environ:
    ONESIGNAL_APP_ID = env.str('ONESIGNAL_APP_ID')

# Twilio Settings
if 'TWILIO_ACCOUNT_SID' in os.environ:
    TWILIO_ACCOUNT_SID = env.str('TWILIO_ACCOUNT_SID')
if 'TWILIO_AUTH_TOKEN' in os.environ:
    TWILIO_AUTH_TOKEN = env.str('TWILIO_AUTH_TOKEN')
if 'TWILIO_PHONE_NUMBER' in os.environ:
    TWILIO_PHONE_NUMBER = env.str('TWILIO_PHONE_NUMBER')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_celery_results',
    'django_celery_beat',
    'import_export',
    'rest_framework',
    'rest_framework.authtoken',
    'privacy_policy',
    'contact',
    'corsheaders',
    'service_requests',
    'page_views',
    'daily_tasks',
    'surveys',
    'fitbit_api',
    'fitbit_authorize',
    'fitbit_activities',
    'behavioral_messages',
    'push_messages',
    'morning_messages',
    'weekly_reflection',
    'weeks',
    'days',
    'locations',
    'weather',
    'randomization',
    'walking_suggestions',
    'walking_suggestion_times',
    'activity_types',
    'activity_logs',
    'activity_plans',
    'activity_summaries',
    'fitbit_activity_logs',
    'anti_sedentary',
    'watch_app',
    'participants',
    'data_export',
    'dashboard',
    'sms_service'
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication'
    ]
}

# Allow JavaScript to return Authorization-Token from Participant#EnrollView
CORS_ALLOW_HEADERS = default_headers + (
    'Authorization-Token',
)
CORS_EXPOSE_HEADERS = ['Authorization-Token']
CORS_ORIGIN_ALLOW_ALL = True

FCM_SERVER_KEY = env('FCM_SERVER_KEY', default='secret-key')

RABBITMQ_HOST = env('RABBITMQ_SERVICE_HOST', default='rabbitmq')
CELERY_BROKER_URL = 'amqp://guest:guest@%s:5672//' % (RABBITMQ_HOST)
CELERY_RESULT_BACKEND = 'django-db'
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'

FIXTURE_DIRS = [
    root('fixtures')
]

ROOT_URLCONF = 'heartsteps.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates/')],
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
