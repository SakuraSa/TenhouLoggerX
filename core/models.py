#!/usr/bin/env python
# coding=utf-8

"""
core.models
"""

__author__ = 'Rnd495'

import datetime

import hashlib
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, DateTime, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from configs import Configs


class _Base(object):
    """
    Base
    """

    def __repr__(self):
        return "<%s>" % type(self).__name__

configs = Configs.instance()
Base = declarative_base(cls=_Base)


class User(Base):
    __tablename__ = 'T_User'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(length=64), nullable=False, unique=True, index=Index('User_index_name'))
    pwd = Column(String(length=128), nullable=False)
    role_id = Column(Integer, nullable=False, index=Index('User_index_role_id'))
    register_time = Column(DateTime, nullable=False)
    header_url = Column(String(length=256), nullable=True)

    def __init__(self, name, pwd,
                 role_id=0,
                 header_url=None):
        self.name = name
        self.pwd = None
        self.register_time = datetime.datetime.now()
        self.role_id = role_id
        self.header_url = header_url

        self.set_password(pwd)

    def __repr__(self):
        return "<User[%s]: %s>" % (self.id, self.name)

    def get_is_same_password(self, password):
        return User.password_hash(password) == self.pwd

    def set_password(self, password):
        self.pwd = hashlib.sha256(self.name + password).hexdigest()


class Role(Base):
    __tablename__ = 'T_Role'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(length=64), nullable=False)

    def __init__(self, name, id=None):
        self.name = name
        if id is not None:
            self.id = id

    def __repr__(self):
        return "<Role[%s]: %s>" % (self.id, self.name)


class PlayerLog(Base):
    __tablename__ = 'T_PlayerLog'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(length=32), nullable=False, index=Index('PlayerLog_index_name'))
    ref = Column(String(length=64), nullable=False, index=Index('PlayerLog_index_ref'))
    time = Column(DateTime, nullable=False, index=Index('PlayerLog_index_time'))

    def __init__(self, name, ref, time):
        self.name = name
        self.ref = ref
        self.time = time

    def __repr__(self):
        return "<%s[%s]: %s-%s>" % (type(self).__name__, self.id, self.name, self.ref)

_engine = None
_session_maker = None
_session = None


def get_engine():
    global _engine
    if not _engine:
        _engine = create_engine(configs.database_url, echo=False)
        Base.metadata.create_all(_engine)
    return _engine


def get_session_maker():
    global _session_maker
    if not _session_maker:
        _session_maker = sessionmaker(bind=get_engine())
    return _session_maker


def get_global_session():
    global _session
    if not _session:
        _session = get_session_maker()()
    return _session


def get_new_session():
    return get_session_maker()()
