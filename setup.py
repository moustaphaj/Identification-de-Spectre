#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name='identification-pic',
    version='0.1',
    author='Moustapha Jaffal',
    author_email='moustapha.jaffal@gmail.com',
    packages=find_packages(),
    install_requires=[
        'pandas', 'matplotlib', 'xlrd'
    ]
)
