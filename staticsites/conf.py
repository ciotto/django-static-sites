# from staticsites import utilities
from staticsites import minify

__author__ = 'Christian Bianciotto'

STATICSITE_DEPLOY_PATH = 'deploy/%(deploy_type)s'

# es. %Y-%m-%d_%H:%M'
STATICSITE_DEPLOY_PATH_DATE_FORMAT = ''

STATICSITE_DEFAULT_DEPLOY_TYPE = 'dev'

STATICSITE_DEFAULTS = {}

STATICSITE_MINIFY_XML = True
STATICSITE_MINIFY_CSS = True
STATICSITE_MINIFY_JS = True

STATICSITE_MINIFY_FUNC = {}

STATICSITE_GZIP = True

STATICSITE_HTML_EXTENSIONS = ['.html', '.htm']
STATICSITE_CSS_EXTENSIONS = ['.css']
STATICSITE_JS_EXTENSIONS = ['.js', '.json']
STATICSITE_XML_EXTENSIONS = ['.xml'] + STATICSITE_HTML_EXTENSIONS


# Set minify correct functions for extensions
for extension in STATICSITE_XML_EXTENSIONS:
    STATICSITE_MINIFY_FUNC[extension] = minify.xml

for extension in STATICSITE_CSS_EXTENSIONS:
    STATICSITE_MINIFY_FUNC[extension] = minify.css

for extension in STATICSITE_JS_EXTENSIONS:
    STATICSITE_MINIFY_FUNC[extension] = minify.js
