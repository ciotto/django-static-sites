from os.path import dirname, join
from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib import admin
from staticsites.utilities import get_default_index, get_deploy_root

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', '{{ project_name }}.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
)

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
