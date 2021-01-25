"""
Django settings for autoelect project.

Generated by 'django-admin startproject' using Django 2.0.5.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.0/ref/settings/
"""

import os
import environ

env = environ.Env()
# reading .env file
environ.Env.read_env()

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY')

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'login',
    'logout',
    'vote',
    'officer',
    'sysadmin',
    'honeypot',
    'admin_honeypot',
    'audit_trail',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'audit_trail.middleware.AuditMiddleware',
]

ROOT_URLCONF = 'autoelect.urls'

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

WSGI_APPLICATION = 'autoelect.wsgi.app'

# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('DATABASE_PRIMARY'),
        'USER': env('DATABASE_USER_PRIMARY'),
        'PASSWORD': env('DATABASE_PASSWORD_PRIMARY'),
        'HOST': env('DATABASE_HOST'),
        'PORT': env('DATABASE_PORT')
    },
    'vote1': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('DATABASE_VOTE') + '1',
        'USER': env('DATABASE_USER_VOTE1'),
        'PASSWORD': env('DATABASE_PASSWORD_VOTE1'),
        'HOST': env('DATABASE_HOST'),
        'PORT': env('DATABASE_PORT')
    },
    'vote2': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('DATABASE_VOTE') + '2',
        'USER': env('DATABASE_USER_VOTE2'),
        'PASSWORD': env('DATABASE_PASSWORD_VOTE2'),
        'HOST': env('DATABASE_HOST'),
        'PORT': env('DATABASE_PORT')
    },
    'vote3': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('DATABASE_VOTE') + '3',
        'USER': env('DATABASE_USER_VOTE3'),
        'PASSWORD': env('DATABASE_PASSWORD_VOTE3'),
        'HOST': env('DATABASE_HOST'),
        'PORT': env('DATABASE_PORT')
    },
}

DATABASE_ROUTERS = [ 'autoelect.dbrouter.PrimaryReplicaRouter' ]

# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

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

AUTH_USER_MODEL = 'vote.AuthUser'

# Internationalization
# https://docs.djangoproject.com/en/2.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = False

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/

STATIC_URL = env('STATIC_PATH')

STATICFILES_DIRS = (os.path.join(BASE_DIR, 'static'),)
# STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# The URL where requests are redirected for login
LOGIN_URL = '/login/'

# The URL where requests are redirected after login
LOGIN_REDIRECT_URL = '/'

# Email settings
EMAIL_HOST = env('EMAIL_HOST')
EMAIL_HOST_USER = env('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')
EMAIL_PORT = int(env('EMAIL_PORT'))
EMAIL_USE_TLS = True

# Session expiry settings
# Voting session expires in 30 minutes
SESSION_COOKIE_AGE = 60 * 30

SESSION_EXPIRE_AT_BROWSER_CLOSE = True

SESSION_SAVE_EVERY_REQUEST = True

# Media settings
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

MEDIA_URL = '/media/'

# Google captcha secret sey 
GOOGLE_RECAPTCHA_SECRET_KEY = env('GOOGLE_RECAPTCHA_SECRET_KEY')

# Logging settings
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'default': {
            'format': '[%(asctime)s] %(message)s'
        }
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'default'
        },
        'httpFile': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs/http.log'),
            'formatter': 'default',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'httpFile'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
