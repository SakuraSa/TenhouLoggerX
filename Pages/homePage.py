#!/usr/bin/env python
# coding = utf-8

"""
Page.homePage
"""

__author__ = 'Rnd495'


from UI.Manager import mapping
from UI.Page import PageBase


@mapping(r'/')
class HomePage(PageBase):
    """
    HomePage
    """
    def get(self):
        self.render('home.html')