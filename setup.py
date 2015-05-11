__author__ = 'Christian Bianciotto'


from setuptools import setup, find_packages
from pip.req import parse_requirements
from pip.download import PipSession


README = open('README.md').read()

install_requires = parse_requirements('requirements.txt', session=PipSession())
install_requires = [str(ir.req) for ir in install_requires]

setup(
    name='django-static-sites',
    version='0.0.3',
    packages=find_packages(),
    package_data={'': ['README.md']},
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
    package_dir={'django-static-admin': 'lib/django-static-admin'},
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: GNU GENERAL PUBLIC LICENSE',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ],
    install_requires=install_requires,
)