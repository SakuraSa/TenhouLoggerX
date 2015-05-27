#!/usr/bin/env python
# coding=utf-8

"""
core.models
"""

__author__ = 'Rnd495'

import datetime
import hashlib
import json

from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, DateTime, Index, Text
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
    lobby = Column(String(length=8), nullable=False, index=Index('PlayerLog_index_lobby'))
    rule = Column(String(length=4), nullable=False, index=Index('PlayerLog_index_rule'))
    size = Column(Integer, nullable=False, index=Index('PlayerLog_index_size'))

    def __init__(self, name, ref, time, lobby, rule, size):
        self.name = name
        self.ref = ref
        self.time = time
        self.lobby = lobby
        self.rule = rule
        self.size = size

    def __repr__(self):
        return "<%s[%s]: %s-%s>" % (type(self).__name__, self.id, self.name, self.ref)


class Cache(Base):
    __tablename__ = 'T_Cache'

    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String(length=64), nullable=False, unique=True, index=Index('Cache_index_key'))
    time = Column(DateTime, nullable=False, index=Index('Cache_index_time'))
    data = Column(Text, nullable=False)

    def __init__(self, key, data):
        self.key = key
        self.data = None
        self.time = datetime.datetime.now()
        self.json = data

    @property
    def json(self):
        return json.loads(self.data)

    @json.setter
    def json(self, value):
        self.data = json.dumps(value)

    @staticmethod
    def get(key, expire_time=None):
        """
        return value from cache
        when key is not found in cache, return None
        when expire_time is set and created time + expire time > now, return None
        :param key: cache key
        :param expire_time: expire time
        :return: cache value
        """
        session = get_new_session()
        cache = session.query(Cache).filter(Cache.key == key).first()

        if cache is not None:
            if expire_time and cache.time + expire_time <= datetime.datetime.now():
                session.delete(cache)
                session.commit()
                value = None
            else:
                value = cache.json
        else:
            value = None
        session.close()
        return value

    @staticmethod
    def set(key, value):
        """
        :param key: cache key
        :param value: cache value
        """
        session = get_new_session()
        with session.no_autoflush:
            cache = Cache(key=key, data=value)
            query = session.query(Cache).filter(Cache.key == cache.key)
            cache = query.first()
            if cache is None:
                cache = Cache(key=key, data=value)
                session.add(cache)
            else:
                cache.key = key
                cache.data = value
                session.merge(cache)
        session.commit()
        session.close()

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
