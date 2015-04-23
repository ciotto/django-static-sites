from django.shortcuts import render_to_response
from django.template import RequestContext
from staticsites.decorators import staticview
from staticsites.utilities import get


@staticview
def index(request, deploy_type=None):
    ctx = {'title': 'Hello world!', 'js_path': get(js__test.path, deploy_type)}

    return render_to_response('index.html', ctx, context_instance=RequestContext(request))


@staticview(path={'demo': 'asd/test.js', '': 'js/test.js'})
def js__test(request):

    ctx = {'title': 'Hello world!'}

    return render_to_response('test.js', ctx, context_instance=RequestContext(request))
