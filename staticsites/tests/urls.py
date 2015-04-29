from os.path import dirname
from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib import admin
from os.path import join
from staticsites.utilities import get_deploy_root, get_default_index

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'staticsites_project2.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
)

# Serve default deploy folder as site root
if settings.DEBUG:
    urlpatterns += patterns('', (
        r'^(?P<path>.*)$',
        'django.views.static.serve',
        {'document_root': join(dirname(settings.BASE_DIR), get_deploy_root()), 'path': get_default_index()}
    ))
