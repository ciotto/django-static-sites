#Hello world

You can launch the deploy server for this sample by `manage.py runserver --settings staticsites.tests.samples.01_hello_world.settings` 
command. The `--settings staticsites.tests.samples.02_hello_world.settings` is necessary only if you want to use 
*staticsites* sample, if you develop on new project is sufficent to use the `manage.py runserver` command.

This sample deploy two simple files using the *Django* template system:

```
deploy/dev
├── index.html
└── js
    └── test.js
```

To do this, you must to add two function in your `views.py` with the `@staticview` decorator:

######views.py:
```python
from django.shortcuts import render_to_response
from django.template import RequestContext
from staticsites.decorators import staticview
from staticsites.conf_dict import DeployTypes


@staticview
def index(request, deploy_type=None):
    ctx = {'title': 'Hello world!', 'js_path': js__test.path.get(deploy_type=deploy_type), 'deploy_type': deploy_type}

    return render_to_response('index.html', ctx, context_instance=RequestContext(request))


@staticview(path=DeployTypes({'demo': 'asd/test.js', '': 'js/test.js'}))
def js__test(request):
    ctx = {'title': 'Hello world!'}

    return render_to_response('test.js', ctx, context_instance=RequestContext(request))

```

The `index` view is a traditional Django's view, except for the `deploy_type=None` parmeter. In order to bind the correct 
javascript file, we must to get the path from the `js__test` view and save it into the context. 

Now, we must to create the `index.html` and `test.js` template files in your templates folder:

######index.html:
```html
<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">

    <script type="text/javascript" src="{{ js_path }}"></script>

    <title>{{ title }}</title>
</head>
<body>
    <h1>{{ title }}</h1>
</body>
</html>
```

######test.js:

```javascript
var text = '{{ title }}';

alert(text);
```

For this simple example we don't need other configuration. If you need to manually testing the deploy procedure is 
sufficient to launch the `virtualenv/bin/python manage.py deploy YOUR_DEPLOY_TYPE --settings staticsites.tests.samples.01_hello_world.settings ` 
command, otherwise when deploy server are running, the site is aumomatically deployed using *dev* configuration.

###Other samples

1. [Hello world](https://github.com/ciotto/django-static-sites/tree/master/staticsites/tests/samples/01_hello_world)
2. [Hello world (with static)](https://github.com/ciotto/django-static-sites/tree/master/staticsites/tests/samples/02_hello_world)
3. [AWS S3/CloudFront](https://github.com/ciotto/django-static-sites/tree/master/staticsites/tests/samples/03_aws)
