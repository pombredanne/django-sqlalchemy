# -*- coding: utf-8 -*-

from sqlalchemy.sql import expression
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.dialects.postgresql import REAL


class Distance(expression.FunctionElement):
    """ Distance method (a <-> b)"""
    type = REAL()
    name = 'distance'


@compiles(Distance)
def default_distance(element, compiler, **kw):
    arg1, arg2 = tuple(element.clauses)
    return "%s <-> %s" % (
        compiler.process(arg1),
        compiler.process(arg2),
    )
