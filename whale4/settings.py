"""
Django settings for whale4 project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# The part to be kept secret
import whale4.secret_settings


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = whale4.secret_settings.SECRET_KEY

DEBUG = False


ALLOWED_HOSTS = ['localhost', 'whale.imag.fr', 'lig-whale.imag.fr']


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'accounts',
    'polls',
    'bootstrap3',
    'polymorphic',

)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.locale.LocaleMiddleware',
)


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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



ROOT_URLCONF = 'whale4.urls'

WSGI_APPLICATION = 'whale4.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = whale4.secret_settings.DATABASES

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

gettext = lambda x: x


LANGUAGES = (
    ('fr', gettext('French')),
    ('en', gettext('English')),
)


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_URL = '/static/'

STATICFILES_DIRS = (os.path.join(BASE_DIR, 'static'), )
APPEND_SLASH = True

LOGIN_URL = 'login'
LOGOUT_URL = 'logout'
LOGIN_REDIRECT_URL = 'home'
LOCALE_PATHS = [os.path.join(BASE_DIR, 'locale'), ]
AUTH_USER_MODEL = 'accounts.WhaleUser'

BOOTSTRAP3 = {
    'horizontal_label_class': 'col-md-4',
    'horizontal_field_class': 'col-md-8',
}

EMAIL_HOST = whale4.secret_settings.EMAIL_HOST
EMAIL_HOST_USER = whale4.secret_settings.EMAIL_HOST_USER
EMAIL_HOST_PASSWORD = whale4.secret_settings.EMAIL_HOST_PASSWORD
EMAIL_PORT = whale4.secret_settings.EMAIL_PORT
EMAIL_USE_TLS = whale4.secret_settings.EMAIL_USE_TLS
EMAIL_BACKEND = whale4.secret_settings.EMAIL_BACKEND
EMAIL_FROM = whale4.secret_settings.EMAIL_FROM

BASE_URL = whale4.secret_settings.BASE_URL

