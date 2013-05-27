#!/usr/bin/env python
# Author: <Chaobin Tang ctang@redhat.com>


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(name = "pycntv",   
      version = '0.0.1',
      description = "Python API utilises cntv.com API to get TV program schedules",
      maintainer = "Chaobin Tang",
      maintainer_email = "cbtchn@gmail.com",
      url = "",
      download_url = "",
      packages = get_packages(),
      scripts = ['',],
      platforms = ["any"],
      license = 'BSD',
      long_description = "Python API utilises cntv.com API to get TV program schedules",
      classifiers=[
          'Development Status :: 4 - Beta',
          'Framework :: Gevent',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: BSD License',
          'Operating System :: OS Independent',   
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: Implementation :: CPython',
          'Topic :: Communications',
          'Topic :: Internet :: WWW/HTTP :: CLI',
          'Topic :: Software Development :: Libraries :: Python Modules'
          ],
     )
