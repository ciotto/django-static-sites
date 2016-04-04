#django-static-sites

*django-static-sites* is an easy to use *Django* app that allow you to create a static sites with the power of Django
template system. You can render an existing *Django* view by adding a decorator or you can create an empty project
optimized for *django-static-sites* use. You can specify multiple configuration for multiple deploy type.

[GitHub](https://github.com/ciotto/django-static-sites)


##How to start

1. install *django-static-sites* in your python path or in your *virtualenv* path
(`pip install https://github.com/ciotto/django-static-sites/archive/master.zip`)
2. create an empty optimized project by `django-static-admin startproject PROJECT_NAME` command
3. move to the `PROJECT_NAME` folder and create site by `python manage.py startsite SITE_NAME` command
4. migrate `python manage.py migrate`
5. deploy `python manage.py deploy`
6. start server `python manage.py runserver`
7. enjoy it at [http://127.0.0.1:8000](http://127.0.0.1:8000) **:-)**


##How to use

If you want to use the *Django* template system, you must to add a function in your `views.py` file and add the
`@staticview` decorator:

```python
@staticview
def index(request):
    ctx = {'title': 'Hello world!'}

    return render_to_response('index.html', ctx, context_instance=RequestContext(request))
```

and the `index.html` template file in your templates folder:

```html
<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">

    <title>{{ title }}</title>
</head>
<body>
    <h1>{{ title }}</h1>
</body>
</html>
```
When you deploy (`python manage.py deploy` or *autodeploy*), *django-static-sites* create the `index.html` using
`index.html` template.

If you want to add an rendered javascript file, you can create a view:

```python
@staticview(path={'demo': 'asd/test.js', '': 'js/test.js'})
def js__test(request):

    ctx = {'title': 'Hello world!'}

    return render_to_response('test.js', ctx, context_instance=RequestContext(request))
```

and the relatine `test.js` template:

```javascript
var text = '{{ title }}';

alert(text);
```

The `test.js` destination path are specified in `@staticview` decorator and is different for different deploy type so
we must add `'js_path': js__test.path.get(deploy_type=deploy_type)` in the `index.html` context. `deploy_type` are passed to the view
functions if is declared. Now we can add the import line in the `index.html` file:

```html
<script type="text/javascript" src="{{ js_path }}"></script>
```

You can see this and more samples in `staticsites/tests/samples` folder; you can launch the deploy server for this 
samples by `manage.py runserver --settings staticsites.tests.samples.SAMPLE_NAME.settings` command.

######Other samples

1. [Hello world](https://github.com/ciotto/django-static-sites/tree/master/staticsites/tests/samples/01_hello_world)
2. [Hello world (with static)](https://github.com/ciotto/django-static-sites/tree/master/staticsites/tests/samples/02_hello_world)
3. [AWS S3/CloudFront](https://github.com/ciotto/django-static-sites/tree/master/staticsites/tests/samples/03_aws)
4. [AWS S3/CloudFront (multiple remote)](https://github.com/ciotto/django-static-sites/tree/master/staticsites/tests/samples/04_aws_multiple_deploy_type)
5. [FTP](https://github.com/ciotto/django-static-sites/tree/master/staticsites/tests/samples/05_ftp)

###Add to an existing project

If you want to integrate `django-static-sites` in existing project you must to:

1. add `staticsites` in your INSTALLED_APPS (replace django.contrib.staticfiles)

If you want to use Django development server to serve the deployed static site:

1. add this lines at your `url.py`

```python
# Serve default deploy folder as site root
if settings.DEBUG:
    urlpatterns += patterns('', (
        r'^(?:%s)?$' % get_default_index(deploy_type='dev'),
        'django.views.static.serve',
         {
            'document_root': get_deploy_root(deploy_type='dev'), 'path': get_default_index(deploy_type='dev')
         }
    ), (
        r'^(?P<path>.*)$',
        'django.views.static.serve',
        {'document_root': get_deploy_root(deploy_type='dev')}
    ))
```


##Remote deploy

*django-static-sites* use the *Django* `Storage` system during the deploy procedure; by default the file are deployed 
locally using `FileSystemStorage`, but you can use any other `Storage` with the correct settings. In the 
[AWS S3/CloudFront](https://github.com/ciotto/django-static-sites/tree/master/staticsites/tests/samples/03_aws) samples 
I use the [django-storages](https://django-storages.readthedocs.org/) AWS storage for deploying on Amazon S3 bucket. 


##ToDo

*django-static-sites* is work-in-progres:

* add automatic url pattern
* ~~autodeploy~~
* ~~static file optimization~~
* revert deploy if fail
* ~~GZip deployed files~~
* ~~minify deployed files~~
* ~~custom header for deployed files~~
* ~~singe configuration constant as dictionary~~
* ~~deploy on multiple remote~~
* add param check and raise Exception
* update tests
* ~~dedicated *settings* module for sample~~
* ~~add tutorials~~
* ~~deploy admin console~~
