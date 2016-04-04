# FTP static site

You can launch the deploy server for this sample by `manage.py runserver --settings staticsites.tests.samples.06_ftp_.settings` 
command. The `--settings staticsites.tests.samples.06_ftp_.settings` is necessary only if you want to use 
*staticsites* sample, if you develop on new project is sufficent to use the `manage.py runserver` command.

In order to launch the sample, you must install [django-storages](https://django-storages.readthedocs.org/) 
(`pip install django-storages`).

This sample deploy four simple files using the *Django* template system and static files on FTP static site:

```
deploy/dev
├── index.html
├── static.html
├── django.png
└── js
    └── test.js
```

To do this, you must to add a setting in your [Hello world (with static)](https://github.com/ciotto/django-static-sites/tree/master/staticsites/tests/samples/02_hello_world) 
`setting.py`:

######FTPStorage configuration
```python
AWS_ACCESS_KEY_ID = 'YOUR_AWS_ACCESS_KEY_ID'
AWS_SECRET_ACCESS_KEY = 'YOUR_AWS_SECRET_ACCESS_KEY'
AWS_STORAGE_BUCKET_NAME = 'YOUR_S3_BUCKET_NAME'
```

This lines are need for configure the `S3BotoStorage`. The `django-storages` library automatically retrieve this 
settings, so we can't use the `conf_dict`.


######Deploy root
```python
from staticsites.conf_dict import DeployTypes
TEST_FTP_CONF = {
    'user': 'YOUR_FTP_USER',
    'password': 'YOUR_FTP_PASSWORD',
    'host': 'YOUR_FTP_HOST',
    'port': 'YOUR_FTP_PORT',
    'path': 'YOUR_FTP_PATH',
}
PROD_FTP_CONF = {
    'user': 'YOUR_FTP_USER',
    'password': 'YOUR_FTP_PASSWORD',
    'host': 'YOUR_FTP_HOST',
    'port': 'YOUR_FTP_PORT',
    'path': 'YOUR_FTP_PATH',
}

STATICSITE_DEPLOY_ROOT = DeployTypes({
    'dev': 'deploy/%(deploy_type)s',
    'test': 'ftp://%(user)s:%(password)s@%(host)s:%(port)s%(path)s' % TEST_FTP_CONF,
    'prod': 'ftp://%(user)s:%(password)s@%(host)s:%(port)s%(path)s' % PROD_FTP_CONF,
})
```

The **FTPStorage** get the username, password, host, port and root path directly from the storage *location*, so you 
probably have 2 different deploy root for test and prod.


######Default storage
```python
from django.core.files.storage import FileSystemStorage
from storages.backends.ftp import FTPStorage
STATICSITE_DEFAULT_FILE_STORAGE = DeployTypes({
    'dev': FileSystemStorage,
    'test': FTPStorage,
    'prod': FTPStorage,
})
```

Now, we tell *django-static-sites* to use `FTPStorage` for *test* deploy.


###Other samples

1. [Hello world](https://github.com/ciotto/django-static-sites/tree/master/staticsites/tests/samples/01_hello_world)
2. [Hello world (with static)](https://github.com/ciotto/django-static-sites/tree/master/staticsites/tests/samples/02_hello_world)
3. [AWS S3/CloudFront](https://github.com/ciotto/django-static-sites/tree/master/staticsites/tests/samples/03_aws)
4. [AWS S3/CloudFront (multiple remote)](https://github.com/ciotto/django-static-sites/tree/master/staticsites/tests/samples/04_aws_multiple_deploy_type)
5. [AWS S3/CloudFront (multiple remote)](https://github.com/ciotto/django-static-sites/tree/master/staticsites/tests/samples/04_aws_multiple_deploy_type)
