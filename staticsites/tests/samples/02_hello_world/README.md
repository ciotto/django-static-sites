#Hello world (with static)

You can launch the deploy server for this sample by `manage.py runserver --settings staticsites.tests.samples.02_hello_world.settings` 
command. The `--settings staticsites.tests.samples.02_hello_world.settings` is necessary only if you want to use 
*staticsites* sample, if you develop on new project is sufficent to use the `manage.py runserver` command.

This sample deploy four simple files using the *Django* template system and static files:

```
deploy/dev
├── index.html
├── static.html
├── django.png
└── js
    └── test.js
```

To do this, you must to add a setting in your [Hello world](https://github.com/ciotto/django-static-sites/tree/master/staticsites/tests/samples/01_hello_world) 
`setting.py`:

```python
STATICSITE_STATICFILES_DIRS = [
    ('PATH_TO_YOUR_STATIC_FILES_FOLDER', ),
]
```

This setting tell *django-static-sites* to copy all file tree in the deploy folder.


###Other samples

1. [Hello world](https://github.com/ciotto/django-static-sites/tree/master/staticsites/tests/samples/01_hello_world)
2. [Hello world (with static)](https://github.com/ciotto/django-static-sites/tree/master/staticsites/tests/samples/02_hello_world)
3. [AWS S3/CloudFront](https://github.com/ciotto/django-static-sites/tree/master/staticsites/tests/samples/03_aws)
4. [AWS S3/CloudFront (multiple remote)](https://github.com/ciotto/django-static-sites/tree/master/staticsites/tests/samples/04_aws_multiple_deploy_type)
