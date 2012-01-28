# -*- coding: utf-8 -*-

import re
from django.utils import simplejson as json

rx_circle_float = re.compile(r'<\(([\d\.\-]*),([\d\.\-]*)\),([\d\.\-]*)>')
rx_line = re.compile(r'\[\(([\d\.\-]*),\s*([\w\.\-]*)\),\s*\(([\d\.\-]*),\s*([\d\.\+]*)\)\]')
rx_point = re.compile(r'\(([\d\.\-]*),\s*([\d\.\-]*)\)')
rx_box = re.compile(r'\(([\d\.\-]*),\s*([\d\.\-]*)\),\s*\(([\d\.\-]*),\s*([\d\.\-]*)\)')
rx_path_identify = re.compile(r'^((?:\(|\[))(.*)(?:\)|\])$')

class Point(tuple):
    """ 
    Class that rep resents of geometric point. 
    """

    def __init__(self, args):
        if len(args) == 2:
            super(Point, self).__init__(args)
        else: 
            raise ValueError("Max is 2 elements")
        self._validate()

    def _validate(self):
        if not isinstance(self.x, (int, long, float)) \
            or not isinstance(self.y, (int, long, float)):
            raise ValueError("invalid data")

    def __repr__(self):
        return "<Point(%s,%s)>" % self

    @property
    def x(self):
        return self[0]
    
    @property
    def y(self):
        return self[1]


class Circle(tuple):
    def __init__(self, args):
        if len(args) == 3:
            super(Circle, self).__init__(args)
        else:
            raise ValueError("invalid data")
        self._validate()

    def _validate(self):
        if not isinstance(self.r, (int, long, float)):
            raise ValueError("invalid data")

    def __repr__(self):
        return "<Circle(%s,%s)>" % (self.point, self.r)

    @property
    def r(self):
        return self[2]

    @property
    def point(self):
        return Point(self[:-1])

    def to_box(self):
        if hasattr(self, '_box'):
            return self._box

        cur = connection.cursor()
        cur.execute("select box(%s) as _;", [self])
        res = cur.fetchone()
        cur.close()

        if not res:
            raise ValueError("Unexpected error")

        self._box = res[0]
        return res[0]


class Lseg(tuple):
    def __init__(self, args):
        if len(args) == 4:
            super(Lseg, self).__init__(args)
        else:
            raise ValueError("invalid content")

    def __iter__(self):
        yield tuple(self.init_point)
        yield tuple(self.end_point)

    def __repr__(self):
        return "<Lseg(%s, %s)>" % \
            (self.init_point, self.end_point)

    @property
    def init_point(self):
        return Point(self[:2])

    @property
    def end_point(self):
        return Point(self[2:])


class Box(tuple):
    def __init__(self, args):
        if len(args) == 4:
            super(Box, self).__init__(args)
        else:
            raise ValueError("invalid content")

    def __repr__(self):
        return "<Box(%s,%s),(%s,%s)>" % self

    @property
    def init_point(self):
        return Point(self[:2])

    @property
    def end_point(self):
        return Point(self[2:])

    @property
    def center_point(self):
        if hasattr(self, '_center_point'):
            return self._center_point

        cur = connection.cursor()
        cur.execute("select @@ %s;", [self])
        res = cur.fetchone()
        cur.close()

        if not res:
            raise ValueError("Unexpected error")

        self._center_point = res[0]
        return res[0]


class Path(tuple):
    closed = False

    def __init__(self, args):
        points = []
        for item in args:
            if isinstance(item, (tuple, list, Point)):
                points.append(tuple(item))
            else:
                points = []
                raise ValueError("invalid content")
        
        self.closed = isinstance(args, tuple)

        if len(points) == 0:
            raise ValueError("invalid content")

        super(Path, self).__init__(points)
    
    def __repr__(self):
        return "<Path(%s) closed=%s>" % (len(self), self.closed)


class Polygon(Path):
    def __repr__(self):
        return "<Polygon(%s) closed=%s>" % (len(self), self.closed)


from psycopg2.extensions import adapt, register_adapter, AsIs, new_type, register_type

""" PYTHON->SQL ADAPTATION """

def adapt_point(point):
    return AsIs(u"point '(%s, %s)'" % (adapt(point.x), adapt(point.y)))

def adapt_circle(c):
    return AsIs(u"circle '<(%s,%s),%s>'" % \
        (adapt(c.point.x), adapt(c.point.y), adapt(c.r)))

def adapt_lseg(l):
    return AsIs(u"'[(%s,%s), (%s,%s)]'::lseg" % (\
        adapt(l.init_point.x),
        adapt(l.init_point.y),
        adapt(l.end_point.x),
        adapt(l.end_point.y)
    ))

def adapt_box(box):
    return AsIs("'(%s,%s),(%s,%s)'::box" % (
        adapt(box.init_point.x),
        adapt(box.init_point.y),
        adapt(box.end_point.x),
        adapt(box.end_point.y)
    ))

def adapt_path(path):
    container = "'[%s]'::path"
    if path.closed:
        container = "'(%s)'::path"
    
    points = ["(%s,%s)" % (x, y) \
        for x, y in path]
    return AsIs(container % (",".join(points)))


def adapt_polygon(path):
    container = "'(%s)'::polygon"
    
    points = ["(%s,%s)" % (x, y) \
        for x, y in path]

    return AsIs(container % (",".join(points)))


register_adapter(Point, adapt_point)
register_adapter(Circle, adapt_circle)
register_adapter(Box, adapt_box)
register_adapter(Path, adapt_path)
register_adapter(Polygon, adapt_polygon)
register_adapter(Lseg, adapt_lseg)
