"""
Django secret settings for whale4 project.
Keep everything in this file secret! Do not push
the non-anonymized file on the public repository!

Rename this file to secret_settings.py to make things work.
"""

DATABASES = {
    'default': {
        'ENGINE': 'db engine here',
        'NAME': 'db name here',
        'USER': 'db user here',
        'PASSWORD': 'db password here',
        'HOST': 'db host here',
        'PORT': '5432' # (change according to your server settings)
    }
}

EMAIL_HOST = 'email server here'
EMAIL_HOST_USER = 'email user name here'
EMAIL_HOST_PASSWORD = 'email account password here'
EMAIL_PORT = 587 # (change according to your server settings)
EMAIL_USE_TLS = True # (change according to your server settings)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

SECRET_KEY = '16 characters secret key here'
