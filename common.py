#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import collections

Point_rgb = collections.namedtuple('Point_rgb', 'r, g, b')

def to_Point_rgb(x):
    return Point_rgb(r = x[0], g = x[1], b = x[2])

def normalize_rgb(point_rgb):
    if not (hasattr(point_rgb, 'r') and hasattr(point_rgb, 'g') and hasattr(point_rgb, 'b')):
        point_rgb = to_Point_rgb(point_rgb)
    sum_all = float(point_rgb.r + point_rgb.g + point_rgb.b)
    return Point_rgb(r = point_rgb.r / sum_all, g = point_rgb.g / sum_all, b = point_rgb.b / sum_all)

def scalar_to_rgba(x):
    return int(x%256), int((x/256)%256), int((x/65536)%256), int((x/16777216)%256)

def rgb_to_scalar(x):
    try:
        return x.b * 256 ** 2 + x.g * 256 + x.r
    except:
        return x[2] * 256 ** 2 + x[1] * 256 + x[0]
