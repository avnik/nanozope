__version__ = '0.1'

import os
import sys

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
try:
    README = open(os.path.join(here, 'README.txt')).read()
    CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()
except IOError:
    README = CHANGES = ''

install_requires=[
    'setuptools',
    'PasteScript',
    'PasteDeploy',
    'zope.component', 
    'zope.configuration',
    'zope.interface', 
    'zope.traversing',
    'zope.security',
    'zope.authentication',
    'zope.processlifetime',
    'repoze.zodbconn',
    ]

setup(name='nanozope',
      version=__version__,
      description='Minimalistic Zope3 publisher',
      long_description=README + '\n\n' +  CHANGES,
      classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Framework :: Zope3",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI",
        "License :: Repoze Public License",
        ],
      keywords='web wsgi zope',
      author="Alexander V. Nikolaev",
      author_email="avn@daemon.hole.ru",
      url="http://github.org/avnik/nanozope",
      packages=find_packages(),
      include_package_data=True,
      namespace_packages = ['nanozope'],
      zip_safe=False,
      install_requires = install_requires,
      extras_require = {
            'test': ['zope.testing'],
      },
      entry_points={
         'paste.app_factory': [
             'main=nanozope.wsgi:make_wsgi_app',
         ],
         'paste.app_install': [
             'main=nanozope.paster:ZopeInstaller',
         ],
      }
)

