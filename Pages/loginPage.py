#!/usr/bin/env python
# coding = utf-8

"""
Pages.loginPage
"""

__author__ = 'Rnd495'


from UI.Manager import mapping
from UI.Page import PageBase
from core.models import get_new_session, User


@mapping(r'/login')
class LoginPage(PageBase):
    """
    LoginPage
    """
    def get(self):
        self.render('login.html', next=self.get_argument('next', '/'))

    def post(self):
        username = self.get_argument('username')
        password = self.get_argument('password')
        remember = self.get_body_argument('remember-me', None)
        expire = 30 if remember else 1
        session = get_new_session()
        user = session.query(User).filter(User.name == username, User.pwd == password).first()
        session.close()
        if not user:
            redirect = self.get_argument('next', '/')
            self.redirect('/login?next=%s' % redirect)
        else:
            self.set_secure_cookie("user_id", str(user.id), expire)
            redirect = self.get_argument('next', '/')
            self.redirect(redirect)