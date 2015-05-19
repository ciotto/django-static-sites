# coding=utf-8
__author__ = 'Christian Bianciotto'


import shutil
import gzip
from django.core.files.storage import FileSystemStorage
from staticsites.conf_dict import BaseDict, DeployTypes, Apps, Extensions
import minify

from os.path import join, isfile, isdir, normcase
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

    reset('STATICSITE_BEFORE_DEPLOY')
    reset('STATICSITE_AFTER_DEPLOY')

    reset('STATICSITE_DEFAULT_DEPLOY_TYPE')
    reset('STATICSITE_DEFAULT_INDEX')

    reset('STATICSITE_GZIP')
    reset('STATICSITE_GZIP_IGNORE_FILES')

    reset('STATICSITE_IGNORE_FILES')
    reset('STATICSITE_IGNORE')

    reset('STATICSITE_ENCODING')

    reset('STATICSITE_HTML_EXTENSIONS')
    reset('STATICSITE_CSS_EXTENSIONS')
    reset('STATICSITE_JS_EXTENSIONS')
    reset('STATICSITE_XML_EXTENSIONS')

    reset('STATICSITE_DEFAULT_FILE_STORAGE')
    reset('STATICSITE_STATICFILES_DIRS')

    reset('STATICSITE_MINIFY_FUNC')
    reset('STATICSITE_MINIFY_IGNORE_FILES')


class TestUtilities(TestCase):
    def test_dict(self):
        d = BaseDict({'foo': 'foo'})
        self.assertRaises(KeyError, d.__getitem__, 'bar')

        d[''] = 'bar'
        self.assertEqual(d['bar'], d[''])

        d = Extensions({
            'foo': 1,
            'bar': 2,
            'qwe': 3,
            '': 4,
        })

        self.assertEqual(d.get(), d[''])
        self.assertEqual(d.get(app='foo'), d[''])
        self.assertEqual(d.get(app='foo', deploy_type='bar'), d[''])
        self.assertEqual(d.get(app='foo', deploy_type='bar', extension='foo'), d['foo'])
        self.assertEqual(d.get(app='foo', extension='foo'), d['foo'])
        self.assertEqual(d.get(app='foo', deploy_type='foo'), d[''])

        d = DeployTypes({
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
        })

        self.assertEqual(d.get(), d[''][''])
        self.assertEqual(d.get(app='foo'), d[''][''])
        self.assertEqual(d.get(app='foo', deploy_type='bar'), d['bar'][''])
        self.assertEqual(d.get(app='foo', deploy_type='bar', extension='foo'), d['bar']['foo'])
        self.assertEqual(d.get(app='foo', extension='foo'), d['']['foo'])
        self.assertEqual(d.get(app='foo', deploy_type='foo'), d[''][''])

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

    def test_get_conf(self):
        reset_all()

        self.assertEqual(utilities.get_conf('STATICSITE_DEFAULT_DEPLOY_TYPE'), conf.STATICSITE_DEFAULT_DEPLOY_TYPE)
        self.assertEqual(utilities.get_conf('STATICSITE_DEPLOY_ROOT', deploy_type='dev'), conf.STATICSITE_DEPLOY_ROOT['dev'])
        self.assertEqual(utilities.get_conf('STATICSITE_DEPLOY_ROOT', deploy_type='test'), conf.STATICSITE_DEPLOY_ROOT[''])

        settings.STATICSITE_DEPLOY_ROOT = 'foo'
        self.assertEqual(utilities.get_conf('STATICSITE_DEPLOY_ROOT'), settings.STATICSITE_DEPLOY_ROOT)
        settings.STATICSITE_DEPLOY_ROOT = DeployTypes({'dev': 'foo', '': 'bar'})
        self.assertEqual(utilities.get_conf('STATICSITE_DEPLOY_ROOT', deploy_type='dev'), settings.STATICSITE_DEPLOY_ROOT['dev'])
        self.assertEqual(utilities.get_conf('STATICSITE_DEPLOY_ROOT', deploy_type='test'), settings.STATICSITE_DEPLOY_ROOT[''])

        dict1 = DeployTypes({'test': 'lol', '': 'qwe'})
        self.assertEqual(utilities.get_conf('STATICSITE_DEPLOY_ROOT', deploy_type='test', input=dict1),
                         dict1['test'])
        self.assertEqual(utilities.get_conf('STATICSITE_DEPLOY_ROOT', deploy_type='demo', input=dict1),
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
        self.assertEqual(utilities.get_path('bar', None, 'test', None), 'bar.html')
        self.assertEqual(utilities.get_path('bar', None, None, None), 'bar.html')
        self.assertEqual(utilities.get_path('foo_bar', None, None, None), 'foo_bar.html')
        self.assertEqual(utilities.get_path('foo__bar',None, None,  None), join('foo', 'bar.html'))
        self.assertEqual(utilities.get_path('foo__bar_asd', None, None, None), join('foo', 'bar_asd.html'))
        self.assertEqual(utilities.get_path('foo__bar__asd', None, None, None), join('foo', 'bar', 'asd.html'))

        # Path is string, return path as is (skip func_name and deploy_type)
        self.assertEqual(utilities.get_path('bar', None, None, 'bar.html'), 'bar.html')
        self.assertEqual(utilities.get_path('foo_bar', None, None, 'bar.html'), 'bar.html')
        self.assertEqual(utilities.get_path('foo__bar', None, None, 'bar.html'), 'bar.html')
        self.assertEqual(utilities.get_path('foo__bar_asd', None, None, 'bar.html'), 'bar.html')
        self.assertEqual(utilities.get_path('foo__bar__asd', None, None, 'bar.html'), 'bar.html')
        self.assertEqual(utilities.get_path('bar', None, None, join('foo', 'bar.html')), join('foo', 'bar.html'))
        self.assertEqual(utilities.get_path('foo_bar', None, None, join('foo', 'bar.html')), join('foo', 'bar.html'))
        self.assertEqual(utilities.get_path('foo__bar', None, None, join('foo', 'bar.html')), join('foo', 'bar.html'))
        self.assertEqual(utilities.get_path('foo__bar_asd', None, None, join('foo', 'bar.html')), join('foo', 'bar.html'))
        self.assertEqual(utilities.get_path('foo__bar__asd', None, None, join('foo', 'bar.html')), join('foo', 'bar.html'))

        # Path is dict, return path[deploy_type] if exist, else return path[''] (skip func_name)
        temp_dict = DeployTypes({'test': 'bar.html', '': 'foo.html'})
        self.assertEqual(utilities.get_path('bar', None, 'test', temp_dict), 'bar.html')
        self.assertEqual(utilities.get_path('foo_bar', None, 'test', temp_dict), 'bar.html')
        self.assertEqual(utilities.get_path('foo__bar', None, 'test', temp_dict), 'bar.html')
        self.assertEqual(utilities.get_path('foo__bar_asd', None, 'test', temp_dict), 'bar.html')
        self.assertEqual(utilities.get_path('foo__bar__asd', None, 'test', temp_dict), 'bar.html')
        self.assertEqual(utilities.get_path('bar', None, 'demo', temp_dict), 'foo.html')
        self.assertEqual(utilities.get_path('foo_bar', None, 'demo', temp_dict), 'foo.html')
        self.assertEqual(utilities.get_path('foo__bar', None, 'demo', temp_dict), 'foo.html')
        self.assertEqual(utilities.get_path('foo__bar_asd', None, 'demo', temp_dict), 'foo.html')
        self.assertEqual(utilities.get_path('foo__bar__asd', None, 'demo', temp_dict), 'foo.html')

        # If path is dict and key missing, raise KeyError
        self.assertRaises(KeyError, utilities.get_path, None, None, 'demo', DeployTypes({'test': 'bar.html'}))

    def test_get_minify(self):
        def func1():
            pass

        def func2():
            pass

        def func3():
            pass

        reset_all()

        self.assertEquals(utilities.get_minify(None, None, 'demo', 'foo.html'), conf.STATICSITE_MINIFY['.html'])
        self.assertEquals(utilities.get_minify(None, None, 'demo', 'foo.css'), conf.STATICSITE_MINIFY['.css'])
        self.assertEquals(utilities.get_minify(None, None, 'demo', 'foo.js'), conf.STATICSITE_MINIFY['.js'])
        self.assertIsNone(utilities.get_minify(None, None, 'demo', 'foo.png'))

        self.assertEquals(utilities.get_minify(DeployTypes({'test': func1, '': func2}), None, 'test', 'foo.html'), func1)
        self.assertEquals(utilities.get_minify(DeployTypes({'test': func1, '': func2}), None, 'demo', 'foo.html'), func2)

        # If minify is dict and key missing, raise KeyError
        self.assertRaises(KeyError, utilities.get_minify, DeployTypes({'test': False}), None, 'demo', 'foo.html')
        self.assertRaises(KeyError, utilities.get_minify, DeployTypes({'test': False}), None, 'demo', 'foo.js')
        self.assertRaises(KeyError, utilities.get_minify, DeployTypes({'test': False}), None, 'demo', 'foo.css')

        # If minify is false, return correct value from settings
        settings.STATICSITE_MINIFY = DeployTypes({
            'test': Extensions({
                '.html': func1,
                '.css': func2,
                '.js': func3,
            }),
            '': Extensions({
                '.html': func2,
                '.css': func3,
                '.js': func1,
            }),
        })
        self.assertEquals(utilities.get_minify(None, None, 'test', 'foo.html'), settings.STATICSITE_MINIFY['test']['.html'])
        self.assertEquals(utilities.get_minify(None, None, 'test', 'foo.css'), settings.STATICSITE_MINIFY['test']['.css'])
        self.assertEquals(utilities.get_minify(None, None, 'test', 'foo.js'), settings.STATICSITE_MINIFY['test']['.js'])
        self.assertEquals(utilities.get_minify(None, None, 'demo', 'foo.html'), settings.STATICSITE_MINIFY['']['.html'])
        self.assertEquals(utilities.get_minify(None, None, 'demo', 'foo.css'), settings.STATICSITE_MINIFY['']['.css'])
        self.assertEquals(utilities.get_minify(None, None, 'demo', 'foo.js'), settings.STATICSITE_MINIFY['']['.js'])

        # If minify is func retur always func
        self.assertEquals(utilities.get_minify(func1, None, None, 'foo.bar'), func1)
        self.assertEquals(utilities.get_minify(func2, None, None, None), func2)

    def test_ignore(self):
        reset_all()

        files = [
            'foo',
            'test/Foo',
            'test/bar/foo',
            'bar',
            'test/bar',
        ]

        settings.STATICSITE_IGNORE_FILES = [
            'foo',
            'test/*',
        ]
        self.assertEquals(sorted(utilities.ignore_files('foo', '', files)), ['test/Foo', 'test/bar', 'foo', 'test/bar/foo'])

        settings.STATICSITE_IGNORE_FILES = [
            'foo',
            '!test/bar/foo',
            'test/*',
        ]
        self.assertEquals(sorted(utilities.ignore_files('foo', '', files)), ['test/Foo', 'test/bar', 'foo'])

        settings.STATICSITE_IGNORE_FILES = [
            'Foo',
            'test/*',
        ]
        self.assertEquals(sorted(utilities.ignore_files('foo', '', files)), ['test/Foo', 'test/bar', 'foo', 'test/bar/foo'])

        settings.STATICSITE_IGNORE_FILES = [
            'Foo',
        ]
        self.assertEquals(sorted(utilities.ignore_files('foo', '', files)), ['test/Foo', 'foo', 'test/bar/foo'])

    def test_deploy(self):
        reset_all()

        base_path = 'deploy/test'

        if isdir(base_path):
            shutil.rmtree(base_path)

        deploy_type = 'test_deploy'

        settings.STATICSITE_DEFAULT_FILE_STORAGE = [
            FileSystemStorage,
            (FileSystemStorage, {'location': base_path + '/%(deploy_type)s_2'}),
        ]
        settings.STATICSITE_DEPLOY_ROOT = base_path + '/%(deploy_type)s'
        settings.STATICSITE_STATICFILES_DIRS = (
            ('staticsites/tests/samples/02_hello_world/static', ),
        )

        deploy(deploy_type)

        self.assertTrue(isfile('%s/%s/index.html' % (base_path, deploy_type)))
        self.assertTrue(isfile('%s/%s/js/test.js' % (base_path, deploy_type)))
        self.assertTrue(isfile('%s/%s/django.png' % (base_path, deploy_type)))
        self.assertTrue(isfile('%s/%s/static.html' % (base_path, deploy_type)))
        self.assertTrue(isfile('%s/%s_2/index.html' % (base_path, deploy_type)))
        self.assertTrue(isfile('%s/%s_2/js/test.js' % (base_path, deploy_type)))
        self.assertTrue(isfile('%s/%s_2/django.png' % (base_path, deploy_type)))
        self.assertTrue(isfile('%s/%s_2/django.png' % (base_path, deploy_type)))

        self.assertEquals(utilities.read_gzip_file('deploy/%s/index.html' % deploy_type),
                          gzip.open('deploy/%s/index.html' % deploy_type).read())

        reset('STATICSITE_STATICFILES_DIRS')

        deploy(deploy_type)

        self.assertTrue(isfile('%s/%s/index.html' % (base_path, deploy_type)))
        self.assertTrue(isfile('%s/%s/js/test.js' % (base_path, deploy_type)))
        self.assertFalse(isfile('%s/%s/static.html' % (base_path, deploy_type)))
        self.assertFalse(isfile('%s/%s/django.png' % (base_path, deploy_type)))
        self.assertTrue(isfile('%s/%s_2/index.html' % (base_path, deploy_type)))
        self.assertTrue(isfile('%s/%s_2/js/test.js' % (base_path, deploy_type)))
        self.assertFalse(isfile('%s/%s_2/django.png' % (base_path, deploy_type)))
        self.assertFalse(isfile('%s/%s_2/django.png' % (base_path, deploy_type)))

        if isdir(base_path):
            shutil.rmtree(base_path)

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
    ° | à | á | â | ã | æ
    </p>
</body>
</html>
'''
        html_min = u'<!DOCTYPE html>\n<html lang="it"><head><meta charset="UTF-8"><title>Test</title></head><body>' \
                   u'<p> ° | à | á | â | ã | æ </p></body></html>'

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
    background: url("°àáâãæ.png");
}

'''
        css_min = u'@-ms-viewport{width:device-width}' \
                  u'@media only screen and (min-device-width:800px){html{overflow:hidden}}html{height:100%;width:100%}' \
                  u'a{color:#e21f18}#test,.test{width:100%;height:100%;background:url("°àáâãæ.png")}'

        self.assertEquals(minify.css(css), css_min)
        self.assertEquals(minify.css(css, comment), ('/* %s */\n' % comment) + css_min)

        js = u'''
/* comment
*/
// comment
function log(message) {
    if (DEBUG && console && console.log) {
        console.log(message);
        console.log('°àáâãæ');
    }
}
'''
        js_min = u'function log(message){if(DEBUG&&console&&console.log){console.log(message);' \
                 u'console.log(\'°àáâãæ\');}}'

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
