#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import common # for normalize_rgb

def linear_combination_index(point_rgb, normalize = False, rw = 1.0, gw = 1.0, bw = 1.0):
    if normalize:
        point_rgb = common.normalize_rgb(point_rgb)
    return rw * point_rgb.r + gw * point_rgb.g + bw * point_rgb.b

def excess_green(point_rgb, normalize = False):
    return linear_combination_index(point_rgb, normalize, rw = -1.0, gw = 2.0, bw = -1.0)

def modified_excess_green(point_rgb, normalize = False):
    return linear_combination_index(point_rgb, normalize, rw = -0.884, gw = 1.262, bw = -0.311)

def excess_red(point_rgb, normalize = False):
    return linear_combination_index(point_rgb, normalize, rw = 1.3, gw = -1.0, bw = 0)

def CIVE(point_rgb, normalize = False):
    return linear_combination_index(point_rgb, normalize, rw = 0.441, gw = -0.811, bw = 0.385) + 18.78745

def VEG(point_rgb, normalize = False):
    a = 0.667
    denominator = point_rgb.r ** a * point_rgb.b ** (1-a)
    if denominator <= 1e-3:
        return point_rgb.g * 1e3
    else:
        return point_rgb.g / denominator

def combination(point_rgb):
    return 0.36 * excess_green(point_rgb) + 0.47 * CIVE(point_rgb) + 0.17 * VEG(point_rgb)
