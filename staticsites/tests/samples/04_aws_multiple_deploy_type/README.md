#AWS S3/CloudFront (multiple remote)

You can launch the deploy server for this sample by `manage.py runserver --settings staticsites.tests.samples.04_aws_multiple_deploy_type.settings` 
command. The `--settings staticsites.tests.samples.04_aws_multiple_deploy_type.settings` is necessary only if you want 
to use *staticsites* sample, if you develop on new project is sufficent to use the `manage.py runserver` command.

In order to launch the sample, you must install [django-storages](https://django-storages.readthedocs.org/) 
(`pip install django-storages`).

This sample deploy four simple files using the *Django* template system and static files on multiple AWS S3 bucket:

```
deploy/dev
├── index.html
├── static.html
├── django.png
└── js
    └── test.js
```

To do this, you must to add another remote in your [AWS S3/CloudFront](https://github.com/ciotto/django-static-sites/tree/master/staticsites/tests/samples/03_aws)
`setting.py`. In particular, we must to clone the *STATICSITE_DEPLOY_ROOT* ant *STATICSITE_AFTER_DEPLOY* settings for
*prod* deploy type. 

After that, we must to remove the *AWS_STORAGE_BUCKET_NAME*, this settings is replaced by e differtent 
*STATICSITE_DEFAULT_FILE_STORAGE* configuration:

```python
STATICSITE_DEFAULT_FILE_STORAGE = DeployTypes({
    '': FileSystemStorage,
    'test': (S3BotoStorage, {'bucket': 'YOUR_CLOUDFRONT_TEST_DISTRIBUTION_ID', 'headers': {'Content-Encoding': 'gzip'}}),
    'prod': (S3BotoStorage, {'bucket': 'YOUR_CLOUDFRONT_PROD_DISTRIBUTION_ID', 'headers': {'Content-Encoding': 'gzip'}}),
})
```

We can pass a bucket name to the *S3BotoStorage* constructor by kwargs dictionary.

######S3BotoStorage configuration
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

STATICSITE_DEPLOY_ROOT = DeployTypes({
    'dev': 'deploy/%(deploy_type)s',
    '': 'deploy/%(deploy_type)s/%(asctime)s',
    'test': '/',
})
```

In order to deploy on the S3 bucket root, we need to set the the `'prod': '/'` in the *STATICSITE_DEPLOY_ROOT* 
*DeployTypes* dictionary. The *DeployTypes* dictionary are used to tell *django-static-sites* to use different 
configuration for different deploy type.


######Default storage
```python
from django.core.files.storage import FileSystemStorage
from storages.backends.s3boto import S3BotoStorage
STATICSITE_DEFAULT_FILE_STORAGE = DeployTypes({
    '': FileSystemStorage,
    'test': S3BotoStorage,
})
```

Now, we tell *django-static-sites* to use `S3BotoStorage` for *test* deploy.


######CloudFront invalidation
```python
AWS_DISTRIBUTION_ID = 'YOUR_CLOUDFRONT_DISTRIBUTION_ID'

from staticsites.utilities import invalidate_paths
STATICSITE_AFTER_DEPLOY = DeployTypes({'': None, 'test': invalidate_paths})
```

Lastly, if you use CloudFront, you must to set the CloudFront distibution ID 
(`AWS_DISTRIBUTION_ID = 'YOUR_CLOUDFRONT_DISTRIBUTION_ID'`) and function *invalidate_paths* as *STATICSITE_AFTER_DEPLOY* 
callback (`STATICSITE_AFTER_DEPLOY = DeployTypes({'': None, 'test': invalidate_paths})`).


###Other samples

1. [Hello world](https://github.com/ciotto/django-static-sites/tree/master/staticsites/tests/samples/01_hello_world)
2. [Hello world (with static)](https://github.com/ciotto/django-static-sites/tree/master/staticsites/tests/samples/02_hello_world)
3. [AWS S3/CloudFront](https://github.com/ciotto/django-static-sites/tree/master/staticsites/tests/samples/03_aws)
4. [AWS S3/CloudFront (multiple remote)](https://github.com/ciotto/django-static-sites/tree/master/staticsites/tests/samples/04_aws_multiple_deploy_type)
