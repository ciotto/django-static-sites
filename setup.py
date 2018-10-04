__author__ = 'Christian Bianciotto'


from setuptools import setup, find_packages
try:
    from pip._internal.req import parse_requirements
    from pip._internal.download import PipSession
except ImportError:
    from pip.req import parse_requirements
    from pip.download import PipSession


README = open('README.md').read()

install_requires = parse_requirements('requirements.txt', session=PipSession())
install_requires = [str(ir.req) for ir in install_requires]

setup(
    name='django-static-sites',
    version='0.0.7',
    packages=find_packages(),
    package_data={'staticsites': ['templates/*/*-tpl', 'templates/*/*/*-tpl']},
    include_package_data=True,
    license='GNU GENERAL PUBLIC LICENSE',
    description='An easy to use Django app to make static site.',
    entry_points={
        'console_scripts': ['django-static-admin=staticsites.management:execute_from_command_line'],
    },
    long_description=README,
    url='https://github.com/ciotto/django-static-sites',
    author='Christian Bianciotto',
    author_email='bianciotto@bitcircle.com',
    package_dir={'django-static-sites': 'lib/django-static-sites'},
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
    ],
    install_requires=install_requires,
)