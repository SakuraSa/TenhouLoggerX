#!/usr/bin/env python
# coding=utf-8

"""
__init__.py
"""

__author__ = 'Rnd495'

import os


# import all *Page.py
for root, dirs, files in os.walk(os.path.split(__file__)[0]):
    for py in (name for name in files if name.endswith("Page.py")):
        __import__('Pages.' + py[:-3])