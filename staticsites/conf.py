from django.core.files.storage import FileSystemStorage
from staticsites import minify

__author__ = 'Christian Bianciotto'

STATICSITE_DEPLOY_ROOT = {'dev': 'deploy/%(deploy_type)s', '': 'deploy/%(deploy_type)s_%(asctime)s'}

STATICSITE_DEPLOY_ROOT_DATE_FORMAT = '%Y-%m-%d_%H.%M.%S'

STATICSITE_DEFAULT_DEPLOY_TYPE = 'dev'
STATICSITE_DEFAULT_INDEX = 'index.html'

STATICSITE_MINIFY_XML = {'dev': False, '': True}
STATICSITE_MINIFY_CSS = {'dev': False, '': True}
STATICSITE_MINIFY_JS = {'dev': False, '': True}

STATICSITE_GZIP = {'dev': False, '': True}

STATICSITE_HTML_EXTENSIONS = ['.html', '.htm']
STATICSITE_CSS_EXTENSIONS = ['.css']
STATICSITE_JS_EXTENSIONS = ['.js', '.json']
STATICSITE_XML_EXTENSIONS = ['.xml'] + STATICSITE_HTML_EXTENSIONS

STATICSITE_DEFAULT_FILE_STORAGE = FileSystemStorage
STATICSITE_STATICFILES_DIRS = None

# Set minify correct functions for extensions
STATICSITE_MINIFY_FUNC = {}
for extension in STATICSITE_XML_EXTENSIONS:
    STATICSITE_MINIFY_FUNC[extension] = minify.xml

for extension in STATICSITE_CSS_EXTENSIONS:
    STATICSITE_MINIFY_FUNC[extension] = minify.css

for extension in STATICSITE_JS_EXTENSIONS:
    STATICSITE_MINIFY_FUNC[extension] = minify.js
