#!/usr/bin/env python
# coding = utf-8

"""
Pages.uploadPage
"""

__author__ = 'Rnd495'

import re

from UI.Manager import mapping
from UI.Page import PageBase
from UI.module.navbar import on_navbar
from core.tenhou.log import Log


TENHOU_REG = re.compile("log=(?P<ref>\d{10}gm-\w{4}-\d{4,5}-\w{8})(&tw=(?P<index>\d))?")


@on_navbar(title='Upload', priority=1)
@mapping(r'/upload')
class UploadPage(PageBase):
    """
    UploadPage
    """
    def get(self):
        self.render('uploadPage.html')

    def post(self):
        logs_text = self.get_argument("logs")
        commands = []
        for match in TENHOU_REG.finditer(logs_text):
            ref, index = match.group('ref'), match.group('index')
            uploaded = Log.check_exists(ref=ref)
            commands.append(UploadCommand(ref=ref, index=index, uploaded=uploaded))
        self.render('uploadResultPage.html', commands=commands)


class UploadCommand(object):
    """
    UploadCommand
    """
    def __init__(self, ref, index, uploaded):
        self.ref = ref
        self.index = index
        self.uploaded = uploaded