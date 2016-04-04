__author__ = 'Christian Bianciotto'


from django.core.files.storage import FileSystemStorage
from staticsites import minify, conf_dict, utilities


STATICSITE_DEPLOY_ROOT = conf_dict.DeployTypes({
    'dev': 'deploy/%(deploy_type)s',
    '': 'deploy/%(deploy_type)s/%(asctime)s'
})

STATICSITE_DEPLOY_ROOT_DATE_FORMAT = '%Y-%m-%d_%H.%M.%S'

STATICSITE_BEFORE_DEPLOY = None
STATICSITE_AFTER_DEPLOY = None

STATICSITE_DEFAULT_DEPLOY_TYPE = 'dev'
STATICSITE_DEFAULT_INDEX = 'index.html'

STATICSITE_GZIP = False
STATICSITE_GZIP_IGNORE_FILES = []

STATICSITE_IGNORE_FILES = [
    # Mac OS x
    '.DS_Store',

    # Windows
    'Thumbs.db',

    # Subversion files
    '.svn',
]
STATICSITE_IGNORE = utilities.ignore_files

STATICSITE_ENCODING = 'UTF-8'

STATICSITE_HTML_EXTENSIONS = ['.html', '.htm']
STATICSITE_CSS_EXTENSIONS = ['.css']
STATICSITE_JS_EXTENSIONS = ['.js', '.json']
STATICSITE_XML_EXTENSIONS = ['.xml'] + STATICSITE_HTML_EXTENSIONS

STATICSITE_DEFAULT_FILE_STORAGE = FileSystemStorage
STATICSITE_STATIC_ROOT = ''
STATICSITE_STATIC_URL = '/'

# Set minify correct functions for extensions
STATICSITE_MINIFY = conf_dict.Extensions({'': None})
for extension in STATICSITE_XML_EXTENSIONS:
    STATICSITE_MINIFY[extension] = minify.xml

for extension in STATICSITE_CSS_EXTENSIONS:
    STATICSITE_MINIFY[extension] = minify.css

for extension in STATICSITE_JS_EXTENSIONS:
    STATICSITE_MINIFY[extension] = minify.js
STATICSITE_MINIFY_IGNORE_FILES = []
