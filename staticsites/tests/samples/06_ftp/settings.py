"""
Django settings for staticsites_project2 project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
from os.path import join

BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'ro7l0ht2*a^@@=hmulzv^v5q-u=cqlr1$t&f8j-il7f^5@diy#'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    # 'django.contrib.staticfiles',

    # This app
    'staticsites',

    # Examples
    'staticsites.tests.samples.03_aws',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'staticsites.tests.urls'

WSGI_APPLICATION = 'staticsites.tests.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(os.path.dirname(os.path.dirname(BASE_DIR)), 'db.sqlite3'),
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_URL = '/static/'


FTP_STORAGE_LOCATION = ''

from django.core.files.storage import FileSystemStorage
from staticsites.conf_dict import DeployTypes
from storages.backends.ftp import FTPStorage

TEST_FTP_CONF = {
    'user': env('TEST_FTP_USER'),
    'password': env('TEST_FTP_PASSWORD'),
    'host': env('TEST_FTP_HOST'),
    'port': env('TEST_FTP_PORT'),
    'path': env('TEST_FTP_PATH'),
}
PROD_FTP_CONF = {
    'user': env('PROD_FTP_USER'),
    'password': env('PROD_FTP_PASSWORD'),
    'host': env('PROD_FTP_HOST'),
    'port': env('PROD_FTP_PORT'),
    'path': env('PROD_FTP_PATH'),
}

STATICSITE_DEPLOY_ROOT = DeployTypes({
    'dev': 'deploy/%(deploy_type)s',
    'test': 'ftp://%(user)s:%(password)s@%(host)s:%(port)s%(path)s' % TEST_FTP_CONF,
    'prod': 'ftp://%(user)s:%(password)s@%(host)s:%(port)s%(path)s' % PROD_FTP_CONF,
})

STATICSITE_DEFAULT_FILE_STORAGE = DeployTypes({
    'dev': FileSystemStorage,
    'test': FTPStorage,
    'prod': FTPStorage,
})

STATICSITE_GZIP = False
