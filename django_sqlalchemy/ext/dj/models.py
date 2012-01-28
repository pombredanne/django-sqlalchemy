# -*- coding: utf-8 -*-

from django_sqlalchemy.declarative import create_base
from django_sqlalchemy.core import engine
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, Boolean, DateTime

from sqlalchemy.sql.expression import text
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method

from django.utils.timezone import now

Base = create_base()

class User(Base):
    __table__ = Table('auth_user', Base.metadata,
        Column('id', Integer, primary_key=True),
        Column('username', String(30), unique=True),
        Column('first_name', String(30), default=''),
        Column('last_name', String(30), default=''),
        Column('email', String(200)),
        Column('password', String(128), default='!'),
        Column('is_staff', Boolean, default=True),
        Column('is_superuser', Boolean, default=True),
        Column('is_active', Boolean, default=True),
        Column('last_login', DateTime(timezone=True), default=now),
        Column('date_joined', DateTime(timezone=True), default=now),
        #autoload=True, autoload_with=engine
    )

    @hybrid_property
    def full_name(self):
        return self.first_name + self.last_name
