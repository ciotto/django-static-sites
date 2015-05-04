
__author__ = 'Christian Bianciotto'


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

    reset('STATICSITE_SETTINGS')

    reset('STATICSITE_DEFAULT_DEPLOY_TYPE')
    reset('STATICSITE_DEFAULT_INDEX')

    reset('STATICSITE_MINIFY_XML')
    reset('STATICSITE_MINIFY_CSS')
    reset('STATICSITE_MINIFY_JS')

    reset('STATICSITE_GZIP')

    reset('STATSTATICSITE_HTML_EXTENSIONSICSITE_GZIP')
    reset('STATICSITE_CSS_EXTENSIONS')
    reset('STATICSITE_JS_EXTENSIONS')
    reset('STATICSITE_XML_EXTENSIONS')

    reset('STATICSITE_DEFAULT_FILE_STORAGE')
    reset('STATICSITE_STATICFILES_DIRS')

    reset('STATICSITE_MINIFY_FUNC')


class TestUtilities(TestCase):
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

    def test_path(self):
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

    def test_minify(self):
        reset_all()

        self.assertEquals(utilities.get_minify(None, 'foo.html', 'demo'), conf.STATICSITE_MINIFY_XML[''])
        self.assertEquals(utilities.get_minify(None, 'foo.css', 'demo'), conf.STATICSITE_MINIFY_CSS[''])
        self.assertEquals(utilities.get_minify(None, 'foo.js', 'demo'), conf.STATICSITE_MINIFY_JS[''])

        self.assertTrue(utilities.get_minify(True, 'foo.html', None))
        self.assertFalse(utilities.get_minify(False, 'foo.html', None))
        self.assertTrue(utilities.get_minify(True, 'foo.bar', None))


        self.assertTrue(utilities.get_minify({'test': True, '': False}, 'foo.html', 'test'))
        self.assertFalse(utilities.get_minify({'test': False, '': True}, 'foo.html', 'test'))
        self.assertFalse(utilities.get_minify({'test': True, '': False}, 'foo.html', 'demo'))
        self.assertTrue(utilities.get_minify({'test': False, '': True}, 'foo.html', 'demo'))

        # If minify is dict and key missing, raise KeyError
        self.assertRaises(KeyError, utilities.get_minify, {'test': False}, 'foo.html', 'demo')
        self.assertRaises(KeyError, utilities.get_minify, {'test': False}, 'foo.js', 'demo')
        self.assertRaises(KeyError, utilities.get_minify, {'test': False}, 'foo.css', 'demo')

        # If minify is false, return correct value from settings
        settings.STATICSITE_MINIFY_XML = {'test': True, '': False}
        settings.STATICSITE_MINIFY_CSS = {'test': False, '': True}
        settings.STATICSITE_MINIFY_JS = {'test': False, '': False}
        self.assertEquals(utilities.get_minify(None, 'foo.html', 'test'), settings.STATICSITE_MINIFY_XML['test'])
        self.assertEquals(utilities.get_minify(None, 'foo.css', 'test'), settings.STATICSITE_MINIFY_CSS['test'])
        self.assertEquals(utilities.get_minify(None, 'foo.js', 'test'), settings.STATICSITE_MINIFY_JS['test'])
        self.assertEquals(utilities.get_minify(None, 'foo.html', 'demo'), settings.STATICSITE_MINIFY_XML[''])
        self.assertEquals(utilities.get_minify(None, 'foo.css', 'demo'), settings.STATICSITE_MINIFY_CSS[''])
        self.assertEquals(utilities.get_minify(None, 'foo.js', 'demo'), settings.STATICSITE_MINIFY_JS[''])

        # If minify is True retur always True
        self.assertTrue(utilities.get_minify(True, 'foo.bar', None))
        self.assertTrue(utilities.get_minify(True, None, None))

    def test_set_settings(self):
        settings.STATICSITE_SETTINGS = {
            'test': {
                'CONSTANT_1': 1,
                'CONSTANT_2': 2,
                'CONSTANT_3': 3,
                },
            '': {
                'CONSTANT_1': 4,
                'CONSTANT_2': 5,
                'CONSTANT_3': 6,
                }
        }

        utilities.set_settings('test')
        self.assertEquals(settings.CONSTANT_1, settings.STATICSITE_SETTINGS['test']['CONSTANT_1'])
        self.assertEquals(settings.CONSTANT_2, settings.STATICSITE_SETTINGS['test']['CONSTANT_2'])
        self.assertEquals(settings.CONSTANT_3, settings.STATICSITE_SETTINGS['test']['CONSTANT_3'])

        utilities.set_settings('demo')
        self.assertEquals(settings.CONSTANT_1, settings.STATICSITE_SETTINGS['']['CONSTANT_1'])
        self.assertEquals(settings.CONSTANT_2, settings.STATICSITE_SETTINGS['']['CONSTANT_2'])
        self.assertEquals(settings.CONSTANT_3, settings.STATICSITE_SETTINGS['']['CONSTANT_3'])

    def test_deploy(self):
        reset_all()

        deploy_type = 'test_deploy'

        settings.STATICSITE_DEPLOY_ROOT = 'deploy/%(deploy_type)s'
        settings.STATICSITE_STATICFILES_DIRS = (
            ('staticsites/tests/examples/example1/static', ),
        )

        deploy(deploy_type)

        self.assertTrue(isfile('deploy/%s/index.html' % deploy_type))
        self.assertTrue(isfile('deploy/%s/js/test.js' % deploy_type))
        self.assertTrue(isfile('deploy/%s/django.png' % deploy_type))

        self.assertEquals(utilities.read_file('deploy/%s/index.html' % deploy_type),
'''<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">

    <script type="text/javascript" src="js/test.js"></script>

    <title>Hello world!</title>
</head>
<body>
    <h1>Hello world!</h1>
    <h2>This is an example for deploy as <i>test_deploy</i>.</h2>

    <p>
        django-static-sites is powered by<br />
        <img src="django.png" />
    </p>
</body>
</html>''')

        reset('STATICSITE_STATICFILES_DIRS')

        deploy(deploy_type)

        self.assertTrue(isfile('deploy/%s/index.html' % deploy_type))
        self.assertTrue(isfile('deploy/%s/js/test.js' % deploy_type))
        self.assertFalse(isfile('deploy/%s/django.png' % deploy_type))
