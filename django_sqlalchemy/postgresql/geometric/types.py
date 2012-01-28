# -*- coding: utf-8 -*-

import sqlalchemy.types as types
from . import *

import re

class PointType(types.UserDefinedType):
    rx = re.compile(r'\(([\d\.\-]*),\s*([\d\.\-]*)\)')

    def get_col_spec(self):
        return 'point'

    def bind_processor(self, dialect):
        return None

    def result_processor(self, dialect, coltype):
        def process(value):
            res =  self.rx.search(value)
            if not res:
                raise ValueError("bad point representation: %r" % value)

            return Point([int(x) if "." not in x else float(x) \
                for x in res.groups()])

        return process


class CircleType(types.UserDefinedType):
    rx = re.compile(r'<\(([\d\.\-]*),([\d\.\-]*)\),([\d\.\-]*)>')

    def get_col_spec(self):
        return 'circle'

    def bind_processor(self, dialect):
        return None

    def result_processor(self, dialect, coltype):
        def process(value):
            if value is None or isinstance(value, Circle):
                return value

            res =  self.rx.search(value)
            if not res:
                raise ValueError("bad point representation: %r" % value)
            
            return Circle([int(x) if "." not in x else float(x) \
                for x in rxres.groups()])

        return process


class BoxType(types.UserDefinedType):
    rx = re.compile(r'\(([\d\.\-]*),\s*([\d\.\-]*)\),\s*\(([\d\.\-]*),\s*([\d\.\-]*)\)')

    def get_col_spec(self):
        return 'box'

    def bind_processor(self, dialect):
        return None

    def result_processor(self, dialect, coltype):
        def process(value):
            print type(value)
            if value is None:
                return value
            
            if isinstance(value, Box):
                return value

            res =  self.rx.search(value)
            if not res:
                raise ValueError("bad point representation: %r" % value)
            
            return Box([int(x) if "." not in x else float(x) \
                for x in res.groups()])

        return process


class PathType(types.UserDefinedType):
    rx = re.compile(r'^((?:\(|\[))(.*)(?:\)|\])$')
    rx_point = re.compile(r'\(([\d\.\-]*),\s*([\d\.\-]*)\)')

    def get_col_spec(self):
        return 'path'

    def bind_processor(self, dialect):
        return None

    def result_processor(self, dialect, coltype):
        def process(value):
            res =  self.rx.search(value)
            if not res:
                raise ValueError("bad point representation: %r" % value)

            is_closed = True if "(" == ident.group(1) else False
            
            return Path([(
                int(x) if "." not in x else float(x), \
                int(y) if "." not in y else float(y) \
            ) for x, y in self.rx_point.findall(points)], closed=is_closed)

        return process
