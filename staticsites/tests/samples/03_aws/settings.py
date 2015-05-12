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

STATIC_ROOT = os.path.join(BASE_DIR, 'deploy/dev')
STATIC_URL = '/static/'

STATICSITE_STATICFILES_DIRS = [
    ('staticsites/tests/samples/03_aws/static', ),
]


# S3BotoStorage configuration
AWS_ACCESS_KEY_ID = 'YOUR_AWS_ACCESS_KEY_ID'
AWS_SECRET_ACCESS_KEY = 'YOUR_AWS_SECRET_ACCESS_KEY'
AWS_STORAGE_BUCKET_NAME = 'YOUR_S3_BUCKET_NAME'

# Sample configuration
from staticsites.conf_dict import DeployTypes

AWS_DISTRIBUTION_ID = 'YOUR_CLOUDFRONT_DISTRIBUTION_ID'

STATICSITE_DEPLOY_ROOT = DeployTypes({
    'dev': 'deploy/%(deploy_type)s',
    '': 'deploy/%(deploy_type)s/%(asctime)s',
    'test': '/',
})

from django.core.files.storage import FileSystemStorage
from storages.backends.s3boto import S3BotoStorage
STATICSITE_DEFAULT_FILE_STORAGE = DeployTypes({
    '': FileSystemStorage,
    'test': (S3BotoStorage, {'headers': {'Content-Encoding': 'gzip'}}),
})

from staticsites.utilities import invalidate_paths
STATICSITE_AFTER_DEPLOY = DeployTypes({'': None, 'test': invalidate_paths})
