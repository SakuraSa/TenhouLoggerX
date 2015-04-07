#!/usr/bin/env python
# coding = utf-8

"""
Pages.uploadPage
"""

__author__ = 'Rnd495'

from UI.Manager import mapping
from UI.Page import PageBase
from UI.module.navbar import on_navbar


@on_navbar(title='Upload', priority=1)
@mapping(r'/upload')
class UploadPage(PageBase):
    """
    UploadPage
    """
    def get(self):
        self.render('uploadPage.html')