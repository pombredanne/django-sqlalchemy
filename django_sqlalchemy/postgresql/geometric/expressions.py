# -*- coding: utf-8 -*-

from sqlalchemy.sql import expression
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.dialects.postgresql import REAL
from sqlalchemy.types import Boolean

from .objects import Box


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


class Overlaps(expression.FunctionElement):
    type = Boolean
    name = 'overlaps'


@compiles(Overlaps)
def default_overlaps(element, compiler, **kw):
    arg1, arg2 = tuple(element.clauses)
    return "%s && %s" % (
        compiler.process(arg1),
        compiler.process(arg2),
    )

class Contains(expression.FunctionElement):
    type = Boolean
    name = 'contains'


@compiles(Contains)
def default_contains(element, compiler, **kw):
    arg1, arg2 = tuple(element.clauses)
    return "%s @> %s" % (
        compiler.process(arg1),
        compiler.process(arg2),
    )

class ToBox(expression.FunctionElement):
    type = Box
    name = 'to_box'

    
@compiles(ToBox)
def default_to_box(element, compiler, **kw):
    if len(element.clauses) > 2:
        raise TypeError("to_box only supports one argument")

    return "box(%s)" % compiler.process(element.clauses)
