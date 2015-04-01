#!/usr/bin/env python
# coding = utf-8

"""
Page.APIPage
"""

__author__ = 'Rnd495'

from UI.Manager import mapping
from UI.Page import PageBase
from core.models import get_new_session, User


@mapping(r'/api/get_username_availability')
class APIGetUsernameAvailability(PageBase):
    """
    APIGetUsernameAvailability
    """
    def get(self):
        username = self.get_argument("username")
        session = get_new_session()
        availability = not bool(session.query(User).filter(User.name == username).count())
        session.close()
        self.write({'ok': True, 'availability': availability})