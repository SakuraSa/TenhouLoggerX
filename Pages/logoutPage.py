#!/usr/bin/env python
# coding = utf-8

"""
Page.logoutPage
"""

__author__ = 'Rnd495'


from UI.Manager import mapping
from UI.Page import PageBase


@mapping(r'/logout')
class LogoutPage(PageBase):
    """
    LogoutPage
    """
    def get(self):
        self.clear_cookie('user_id')
        self.redirect('/')