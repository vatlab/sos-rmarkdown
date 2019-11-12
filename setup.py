#!/usr/bin/env python
#
# Copyright (c) Bo Peng and the University of Texas MD Anderson Cancer Center
# Distributed under the terms of the 3-clause BSD License.

import os
import sys

from setuptools import find_packages, setup

# obtain version of SoS
with open('src/sos_rmarkdown/_version.py') as version:
    for line in version:
        if line.startswith('__version__'):
            __version__ = eval(line.split('=')[1])
            break

CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))


def get_long_description():
    with open(os.path.join(CURRENT_DIR, "README.md"), "r") as ld_file:
        return ld_file.read()


setup(
    name="sos-rmarkdown",
    version=__version__,
    description='A Rmarkdown to SoS Notebook converter',
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    author='Bo Peng',
    url='https://github.com/vatlab/sos-rmarkdown',
    author_email='bpeng@mdanderson.org',
    maintainer='Bo Peng',
    maintainer_email='bpeng@mdanderson.org',
    license='3-clause BSD',
    include_package_data=True,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Science/Research',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
    ],
    zip_safe=False,
    packages=find_packages('src'),
    package_dir={'': 'src'},
    python_requires='>=3.6',
    install_requires=[
        'sos>=0.20.8',
        'sos-notebook>=0.20.9',
        'sos-r',
        'markdown-kernel',
        'papermill',
        'sos-papermill',
        'nbformat',
        'nbconvert>=5.1.1',        
    ],
    entry_points='''
[sos_converters]
rmd-ipynb.parser = sos_rmarkdown.converter:get_Rmarkdown_to_notebook_parser
rmd-ipynb.func = sos_rmarkdown.converter:Rmarkdown_to_notebook

rmd-html.parser = sos_rmarkdown.converter:get_Rmarkdown_to_html_parser
rmd-html.func = sos_rmarkdown.converter:Rmarkdown_to_html
''')
