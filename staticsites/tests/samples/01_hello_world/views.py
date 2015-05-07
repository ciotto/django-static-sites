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
