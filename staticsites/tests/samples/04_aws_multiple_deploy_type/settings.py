"""
Django settings for staticsites_project2 project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os


BASE_DIR = os.path.dirname(os.path.dirname(__file__))


import environ

root = environ.Path(__file__) - 3
base = environ.Path(__file__) - 2
# This points to the directory containing all the project code
SITE_ROOT = root()
BASE_ROOT = base()

env = environ.Env()
# reading .env file
environ.Env.read_env(os.path.join(SITE_ROOT, '.env'))


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
    'django.contrib.staticfiles',

    # This app
    'staticsites',

    # Examples
    'staticsites.tests.samples.04_aws_multiple_deploy_type',
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

# S3BotoStorage configuration
AWS_ACCESS_KEY_ID = env('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = env('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = env('AWS_STORAGE_BUCKET_NAME')

# Sample configuration
from staticsites.conf_dict import DeployTypes

STATICSITE_DEPLOY_ROOT = DeployTypes({
    'dev': 'deploy/%(deploy_type)s',
    '': 'deploy/%(deploy_type)s/%(asctime)s',
    'test': '/',
    'prod': '/',
})

from django.core.files.storage import FileSystemStorage
from storages.backends.s3boto import S3BotoStorage
STATICSITE_DEFAULT_FILE_STORAGE = DeployTypes({
    '': FileSystemStorage,
    'test': (S3BotoStorage, {'bucket': env('AWS_CLOUDFRONT_TEST_DISTRIBUTION_ID'), 'headers': {'Content-Encoding': 'gzip'}}),
    'prod': (S3BotoStorage, {'bucket': env('AWS_CLOUDFRONT_PROD_DISTRIBUTION_ID'), 'headers': {'Content-Encoding': 'gzip'}}),
})

from staticsites.utilities import invalidate_paths
STATICSITE_AFTER_DEPLOY = DeployTypes({'': None, 'test': invalidate_paths, 'prod': invalidate_paths})
