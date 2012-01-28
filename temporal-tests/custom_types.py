# -*- coding: utf-8 -*-

import sys
sys.path.insert(0, '..')

from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey
from sqlalchemy.dialects.postgresql import REAL
from sqlalchemy import create_engine
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql import func
from sqlalchemy.sql import expression

import django_sqlalchemy.postgresql.geometric as g
import sqlalchemy.types as types
import re

# create function expresion

class Distance(expression.FunctionElement):
    type = REAL()
    name = 'distance'


@compiles(Distance)
def default_distance(element, compiler, **kw):
    arg1, arg2 = tuple(element.clauses)
    return "%s <-> %s" % (
        compiler.process(arg1),
        compiler.process(arg2),
    )


engine = create_engine('postgresql://niwi@localhost/test')
metadata = MetaData()
metadata.bind = engine

class PointType(types.TypeEngine):
    __visit_name__ = "POINT"
    
    rx = re.compile(r'\(([\d\.\-]*),\s*([\d\.\-]*)\)')

    def get_col_spec(self):
        return "point"

    def bind_processor(self, dialect):
        def process(value):
            return value
        return process

    def result_processor(self, dialect, coltype):
        def process(value):
            res =  self.rx.search(value)
            if not res:
                raise ValueError("bad point representation: %r" % value)

            return g.Point([int(x) if "." not in x else float(x) \
                for x in res.groups()])

        return process


table = Table('foo', metadata,
    Column('id', Integer, primary_key=True),
    Column('p', PointType),
)

metadata.create_all()

from sqlalchemy.sql import bindparam

q = table.select().where(
    Distance(table.c.p, bindparam('_point', type_=PointType)) == bindparam('_num')
)

c = engine.connect()
