# -*- coding: utf-8 -*-

import sys
sys.path.insert(0, '..')

from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey
from sqlalchemy.dialects.postgresql import REAL
from sqlalchemy import create_engine, select
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql import expression, func

from django_sqlalchemy.postgresql.geometric import *
import sqlalchemy.types as types
import re

# create function expresion

class Distance(expression.FunctionElement):
    type = None
    name = 'distance'

class CenterPoint(expression.FunctionElement):
    type = None
    name = 'center'

@compiles(Distance)
def default_distance(element, compiler, **kw):
    arg1, arg2 = tuple(element.clauses)
    return "%s <-> %s" % (
        compiler.process(arg1),
        compiler.process(arg2),
    )


@compiles(CenterPoint)
def default_center(element, compiler, **kw):
    arg1 = tuple(element.clauses)[0]
    return "@@ %s" % (compiler.process(arg1))



engine = create_engine('postgresql://niwi@localhost/test')
q = select([
    Distance(Point([0,0]), Point([0,2])),
    CenterPoint(Circle([0,2,3])),
])

print str(q)
c = engine.connect()
r = c.execute(q)

print list(r)
c.close()


print str(q)

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


