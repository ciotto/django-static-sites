# coding=utf-8
__author__ = 'Christian Bianciotto'


import gzip
from django.core.files.storage import FileSystemStorage
from conf_dict import BaseDict, DeployTypes, Apps, Extensions
import minify

from os.path import join, isfile
from staticsites import conf
from django.conf import settings
from django.test import TestCase
from staticsites import utilities
from staticsites.deploy import deploy


def reset(attr):
    if hasattr(settings, attr):
        delattr(settings, attr)


def reset_all():
    reset('STATICSITE_DEPLOY_ROOT')

    reset('STATICSITE_DEPLOY_ROOT_DATE_FORMAT')

    reset('STATICSITE_DEFAULT_DEPLOY_TYPE')
    reset('STATICSITE_DEFAULT_INDEX')

    reset('STATICSITE_GZIP')

    reset('STATSTATICSITE_HTML_EXTENSIONSICSITE_GZIP')
    reset('STATICSITE_CSS_EXTENSIONS')
    reset('STATICSITE_JS_EXTENSIONS')
    reset('STATICSITE_XML_EXTENSIONS')

    reset('STATICSITE_DEFAULT_FILE_STORAGE')
    reset('STATICSITE_STATICFILES_DIRS')

    reset('STATICSITE_MINIFY_FUNC')


class TestUtilities(TestCase):
    def test_dict(self):
        d = BaseDict({'foo': 'foo'})
        self.assertRaises(KeyError, d.__getitem__, 'bar')

        d[''] = 'bar'
        self.assertEqual(d['bar'], d[''])

        d = Apps({
            'foo': DeployTypes({
                'bar': Extensions({
                    'foo': 1,
                    'bar': 2,
                    'qwe': 3,
                    '': 4,
                }),
                'qwe': 5,
                '': Extensions({
                    'foo': 6,
                    'bar': 7,
                    'qwe': 8,
                    '': 9,
                }),
            }),
            'bar': Extensions({
                'foo': 10,
                'bar': 11,
                'qwe': 12,
                '': 13,
            }),
            'qwe': 14,
            '': 15,
        })

        self.assertEqual(d.get(), d[''])
        self.assertEqual(d.get(app='foo'), d['foo'][''][''])
        self.assertEqual(d.get(app='foo', deploy_type='bar'), d['foo']['bar'][''])
        self.assertEqual(d.get(app='foo', deploy_type='bar', extension='foo'), d['foo']['bar']['foo'])
        self.assertEqual(d.get(app='foo', extension='foo'), d['foo']['']['foo'])
        self.assertEqual(d.get(app='foo', deploy_type='foo'), d['foo'][''][''])



    def test_get(self):
        reset_all()

        dict1 = {'test': 'lol', '': 'qwe'}
        self.assertEqual(utilities.get(dict1, 'test'), dict1['test'])
        self.assertEqual(utilities.get(dict1, ''), dict1[''])
        self.assertEqual(utilities.get(dict1, 'bar'), dict1[''])

        self.assertRaises(KeyError, utilities.get, {'test': 'lol'}, 'bar')
        self.assertRaises(KeyError, utilities.get, {'test': 'lol'}, None)

    def test_get_conf(self):
        reset_all()

        self.assertEqual(utilities.get_conf('STATICSITE_DEFAULT_DEPLOY_TYPE'), conf.STATICSITE_DEFAULT_DEPLOY_TYPE)
        self.assertEqual(utilities.get_conf('STATICSITE_DEPLOY_ROOT', 'dev'), conf.STATICSITE_DEPLOY_ROOT['dev'])
        self.assertEqual(utilities.get_conf('STATICSITE_DEPLOY_ROOT', 'test'), conf.STATICSITE_DEPLOY_ROOT[''])

        settings.STATICSITE_DEPLOY_ROOT = 'foo'
        self.assertEqual(utilities.get_conf('STATICSITE_DEPLOY_ROOT'), settings.STATICSITE_DEPLOY_ROOT)
        settings.STATICSITE_DEPLOY_ROOT = {'dev': 'foo', '': 'bar'}
        self.assertEqual(utilities.get_conf('STATICSITE_DEPLOY_ROOT', 'dev'), settings.STATICSITE_DEPLOY_ROOT['dev'])
        self.assertEqual(utilities.get_conf('STATICSITE_DEPLOY_ROOT', 'test'), settings.STATICSITE_DEPLOY_ROOT[''])

        dict1 = {'test': 'lol', '': 'qwe'}
        self.assertEqual(utilities.get_conf('STATICSITE_DEPLOY_ROOT', 'test', dict1),
                         dict1['test'])
        self.assertEqual(utilities.get_conf('STATICSITE_DEPLOY_ROOT', 'demo', dict1),
                         dict1[''])

        self.assertEqual(utilities.get_conf('STATICSITE_DEPLOY_ROOT_DATE_FORMAT'), conf.STATICSITE_DEPLOY_ROOT_DATE_FORMAT)
        settings.STATICSITE_DEPLOY_ROOT_DATE_FORMAT = 'foo'
        self.assertEqual(utilities.get_conf('STATICSITE_DEPLOY_ROOT_DATE_FORMAT'), settings.STATICSITE_DEPLOY_ROOT_DATE_FORMAT)

    def test_has_extension(self):
        reset_all()

        self.assertRaises(ValueError, utilities.has_extension, None, [])
        self.assertRaises(ValueError, utilities.has_extension, 'foo/bar.js', None)
        self.assertRaises(ValueError, utilities.has_extension, '', [])

        self.assertFalse(utilities.has_extension(join('foo', 'bar.js'), []))

        self.assertTrue(utilities.has_extension(join('foo', 'bar.htm'), ['.htm', '.html']))
        self.assertTrue(utilities.has_extension(join('foo', 'bar.html'), ['.htm', '.html']))
        self.assertFalse(utilities.has_extension(join('foo', 'bar.js'), ['.htm', '.html']))

    def test_get_path(self):
        reset_all()

        # No path, use func_name (skip deploy_type)
        self.assertEqual(utilities.get_path(None, 'bar', 'test'), 'bar.html')
        self.assertEqual(utilities.get_path(None, 'bar', None), 'bar.html')
        self.assertEqual(utilities.get_path(None, 'foo_bar', None), 'foo_bar.html')
        self.assertEqual(utilities.get_path(None, 'foo__bar', None), join('foo', 'bar.html'))
        self.assertEqual(utilities.get_path(None, 'foo__bar_asd', None), join('foo', 'bar_asd.html'))
        self.assertEqual(utilities.get_path(None, 'foo__bar__asd', None), join('foo', 'bar', 'asd.html'))

        # Path is string, return path as is (skip func_name and deploy_type)
        self.assertEqual(utilities.get_path('bar.html', 'bar', None), 'bar.html')
        self.assertEqual(utilities.get_path('bar.html', 'foo_bar', None), 'bar.html')
        self.assertEqual(utilities.get_path('bar.html', 'foo__bar', None), 'bar.html')
        self.assertEqual(utilities.get_path('bar.html', 'foo__bar_asd', None), 'bar.html')
        self.assertEqual(utilities.get_path('bar.html', 'foo__bar__asd', None), 'bar.html')
        self.assertEqual(utilities.get_path(join('foo', 'bar.html'), 'bar', None), join('foo', 'bar.html'))
        self.assertEqual(utilities.get_path(join('foo', 'bar.html'), 'foo_bar', None), join('foo', 'bar.html'))
        self.assertEqual(utilities.get_path(join('foo', 'bar.html'), 'foo__bar', None), join('foo', 'bar.html'))
        self.assertEqual(utilities.get_path(join('foo', 'bar.html'), 'foo__bar_asd', None), join('foo', 'bar.html'))
        self.assertEqual(utilities.get_path(join('foo', 'bar.html'), 'foo__bar__asd', None), join('foo', 'bar.html'))

        # Path is dict, return path[deploy_type] if exist, else return path[''] (skip func_name)
        self.assertEqual(utilities.get_path({'test': 'bar.html', '': 'foo.html'}, 'bar', 'test'), 'bar.html')
        self.assertEqual(utilities.get_path({'test': 'bar.html', '': 'foo.html'}, 'foo_bar', 'test'), 'bar.html')
        self.assertEqual(utilities.get_path({'test': 'bar.html', '': 'foo.html'}, 'foo__bar', 'test'), 'bar.html')
        self.assertEqual(utilities.get_path({'test': 'bar.html', '': 'foo.html'}, 'foo__bar_asd', 'test'), 'bar.html')
        self.assertEqual(utilities.get_path({'test': 'bar.html', '': 'foo.html'}, 'foo__bar__asd', 'test'), 'bar.html')
        self.assertEqual(utilities.get_path({'test': 'bar.html', '': 'foo.html'}, 'bar', 'demo'), 'foo.html')
        self.assertEqual(utilities.get_path({'test': 'bar.html', '': 'foo.html'}, 'foo_bar', 'demo'), 'foo.html')
        self.assertEqual(utilities.get_path({'test': 'bar.html', '': 'foo.html'}, 'foo__bar', 'demo'), 'foo.html')
        self.assertEqual(utilities.get_path({'test': 'bar.html', '': 'foo.html'}, 'foo__bar_asd', 'demo'), 'foo.html')
        self.assertEqual(utilities.get_path({'test': 'bar.html', '': 'foo.html'}, 'foo__bar__asd', 'demo'), 'foo.html')

        # If path is dict and key missing, raise KeyError
        self.assertRaises(KeyError, utilities.get_path, {'test': 'bar.html'}, None, 'demo')

    def test_get_minify(self):
        def func1():
            pass

        def func2():
            pass

        def func3():
            pass

        reset_all()

        self.assertEquals(utilities.get_minify(None, 'foo.html', 'demo'), conf.STATICSITE_MINIFY['.html'])
        self.assertEquals(utilities.get_minify(None, 'foo.css', 'demo'), conf.STATICSITE_MINIFY['.css'])
        self.assertEquals(utilities.get_minify(None, 'foo.js', 'demo'), conf.STATICSITE_MINIFY['.js'])
        self.assertIsNone(utilities.get_minify(None, 'foo.png', 'demo'))

        self.assertEquals(utilities.get_minify({'test': func1, '': func2}, 'foo.html', 'test'), func1)
        self.assertEquals(utilities.get_minify({'test': func1, '': func2}, 'foo.html', 'demo'), func2)

        # If minify is dict and key missing, raise KeyError
        self.assertRaises(KeyError, utilities.get_minify, {'test': False}, 'foo.html', 'demo')
        self.assertRaises(KeyError, utilities.get_minify, {'test': False}, 'foo.js', 'demo')
        self.assertRaises(KeyError, utilities.get_minify, {'test': False}, 'foo.css', 'demo')

        # If minify is false, return correct value from settings
        settings.STATICSITE_MINIFY = {
            'test': {
                '.html': func1,
                '.css': func2,
                '.js': func3,
            },
            '': {
                '.html': func2,
                '.css': func3,
                '.js': func1,
            }
        }
        self.assertEquals(utilities.get_minify(None, 'foo.html', 'test'), settings.STATICSITE_MINIFY['test']['.html'])
        self.assertEquals(utilities.get_minify(None, 'foo.css', 'test'), settings.STATICSITE_MINIFY['test']['.css'])
        self.assertEquals(utilities.get_minify(None, 'foo.js', 'test'), settings.STATICSITE_MINIFY['test']['.js'])
        self.assertEquals(utilities.get_minify(None, 'foo.html', 'demo'), settings.STATICSITE_MINIFY['']['.html'])
        self.assertEquals(utilities.get_minify(None, 'foo.css', 'demo'), settings.STATICSITE_MINIFY['']['.css'])
        self.assertEquals(utilities.get_minify(None, 'foo.js', 'demo'), settings.STATICSITE_MINIFY['']['.js'])

        # If minify is func retur always func
        self.assertEquals(utilities.get_minify(func1, 'foo.bar', None), func1)
        self.assertEquals(utilities.get_minify(func2, None, None), func2)

    def test_deploy(self):
        reset_all()

        deploy_type = 'test_deploy'

        settings.STATICSITE_DEFAULT_FILE_STORAGE = [
            FileSystemStorage,
            (FileSystemStorage, {'location': 'deploy/example'}),
        ]
        settings.STATICSITE_DEPLOY_ROOT = 'deploy/%(deploy_type)s'
        settings.STATICSITE_STATICFILES_DIRS = (
            ('staticsites/tests/examples/example1/static', ),
        )

        deploy(deploy_type)

        self.assertTrue(isfile('deploy/%s/index.html' % deploy_type))
        self.assertTrue(isfile('deploy/%s/js/test.js' % deploy_type))
        self.assertTrue(isfile('deploy/%s/django.png' % deploy_type))
        self.assertTrue(isfile('deploy/example/index.html'))
        self.assertTrue(isfile('deploy/example/js/test.js'))
        self.assertTrue(isfile('deploy/example/django.png'))

        self.assertEquals(utilities.read_gzip_file('deploy/%s/index.html' % deploy_type),
                          gzip.open('deploy/%s/index.html' % deploy_type).read())

        reset('STATICSITE_STATICFILES_DIRS')

        deploy(deploy_type)

        self.assertTrue(isfile('deploy/%s/index.html' % deploy_type))
        self.assertTrue(isfile('deploy/%s/js/test.js' % deploy_type))
        self.assertFalse(isfile('deploy/%s/django.png' % deploy_type))
        self.assertTrue(isfile('deploy/example/index.html'))
        self.assertTrue(isfile('deploy/example/js/test.js'))
        self.assertFalse(isfile('deploy/example/django.png'))

    def test_minify(self):
        reset_all()

        comment = 'My comment'

        html = u'''
<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">

    <title>Test</title>
</head>
<body>
    <p>
    °é*§çé§ç:ç*
    </p>
</body>
</html>
'''
        html_min = u'<!DOCTYPE html>\n<html lang="it"><head><meta charset="UTF-8"><title>Test</title></head><body>' \
                   u'<p> °é*§çé§ç:ç* </p></body></html>'

        self.assertEquals(minify.xml(html), html_min)
        self.assertEquals(minify.xml(html, comment), ('<!-- %s -->\n' % comment) + html_min)

        css = u'''
/* comment
*/
@-ms-viewport { width: device-width; }
@media only screen and (min-device-width: 800px) {
    html {
        overflow: hidden;
    }
}

html {
    height: 100%;


    width: 100%;
}

a {
    color:      #e21f18;
}

#test, .test     {
    width: 100%;


    height: 100%;
    background: url("°é*§çé§ç:ç*.png");
}

'''
        css_min = u'@-ms-viewport{width:device-width}' \
                  u'@media only screen and (min-device-width:800px){html{overflow:hidden}}html{height:100%;width:100%}' \
                  u'a{color:#e21f18}#test,.test{width:100%;height:100%;background:url("°é*§çé§ç:ç*.png")}'

        self.assertEquals(minify.css(css), css_min)
        self.assertEquals(minify.css(css, comment), ('/* %s */\n' % comment) + css_min)

        js = u'''
/* comment
*/
// comment
function log(message) {
    if (DEBUG && console && console.log) {
        console.log(message);
        console.log('°é*§çé§ç:ç*');
    }
}
'''
        js_min = u'function log(message){if(DEBUG&&console&&console.log){console.log(message);' \
                 u'console.log(\'°é*§çé§ç:ç*\');}}'

        self.assertEquals(minify.js(js), js_min)
        self.assertEquals(minify.js(js, comment), ('/* %s */\n' % comment) + js_min)

    def test_deploy_before_after(self):
        reset_all()

        deploy_type = 'test_deploy'

        settings.STATICSITE_DEPLOY_ROOT = 'deploy/%(deploy_type)s'

        def before(*args, **kwargs):
            sequence.append('before')

        def after(*args, **kwargs):
            sequence.append('after')

        sequence = []
        deploy(deploy_type)
        self.assertEquals(sequence, [])

        sequence = []
        settings.STATICSITE_BEFORE_DEPLOY = before
        deploy(deploy_type)
        self.assertEquals(sequence, ['before'])

        sequence = []
        settings.STATICSITE_AFTER_DEPLOY = after
        deploy(deploy_type)
        self.assertEquals(sequence, ['before', 'after'])

    def test_storage_dump_load(self):
        storage = FileSystemStorage(location='foo/bar')

        dump = utilities.dump_storage(storage)
        loaded_storage = utilities.load_storage(dump)

        self.assertEquals(type(storage), type(loaded_storage))
        self.assertEquals(storage.location, loaded_storage.location)
