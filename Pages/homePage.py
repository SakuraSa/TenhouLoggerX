#!/usr/bin/env python
# coding = utf-8

"""
Pages.homePage
"""

__author__ = 'Rnd495'


from UI.Manager import mapping
from UI.Page import PageBase
from UI.module.navbar import on_navbar


@on_navbar(title='Home', priority=0)
@mapping(r'/')
class HomePage(PageBase):
    """
    HomePage
    """
    def get(self):
        self.render('home.html')