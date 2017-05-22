#! /usr/bin/python

"""
This script installs watchall.

watchall execute a program periodically, showing output fullscreen same as linux watch command
but with scrolling feature
"""

__author__ = 'M. Fatemipour'
__email__ = 'm.fatemipour@gmail.com'
__date__ = '2017-May-10'
__version__ = '2.1.0'

PROJECT = 'watchall'

from setuptools import setup, find_packages
import os

try:
    long_description = open('README.md', 'r').read()
except IOError:
      long_description = 'watchall execute a program periodically, showing output fullscreen same as linux watch command' \
                        'but with scrolling feature'



setup(
    name=PROJECT,
    version=__version__,
    description='execute a program periodically, showing output scrollable fullscreen.',
    long_description=long_description,
    author=__author__,
    author_email=__email__,
    classifiers=['Programming Language :: Python',
                 'Programming Language :: Python :: 2',
                 'Programming Language :: Python :: 2.7',
                 'Intended Audience :: Developers',
                 'Environment :: Console',
                 ],
    packages=find_packages(),
    platforms=['Any'],
    include_package_data=True,
    install_requires=['psutil'],
    scripts=['watchall']
)




