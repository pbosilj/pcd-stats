#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import common # for to_Point_rgb
import mayavi
import os
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from pandas.tools.plotting import scatter_matrix
import numpy
from mayavi import mlab
from mayavi import tools
from scipy.ndimage.filters import gaussian_filter
from itertools import chain
import collections

import matplotlib

values_rgb = numpy.mgrid[0:256, 0:256, 0:256]
lut_rgb = numpy.vstack((values_rgb[0].reshape(1, 256**3), values_rgb[1].reshape(1, 256**3), values_rgb[2].reshape(1, 256**3), 255*numpy.ones((1, 256**3)))).T.astype('int32')

def add_index(cloud, index, name = 'index'):
    cloud[name] = map(index, map(common.to_Point_rgb, zip(cloud.r, cloud.g, cloud.b)))
    return cloud

def combine_clouds(cloud_list):
    cloud = pandas.concat(cloud_list, ignore_index=True)
    cloud.reset_index(drop = True, inplace = True)
    return cloud

def filter_cloud(cloud, low, high, cmin = None, cmax = None, both = False):

    if not cmin or not cmax or both:
        quant = cloud.quantile([low, high, 0.01, 0.99])
        cloud = cloud.apply (lambda x : x[(x > quant.loc[low, x.name]) & (x < quant.loc[high, x.name])], axis = 0)
        if 'VEG' in cloud.keys():
            vmin = quant.loc[0.01, 'VEG']
            vmax = quant.loc[0.99, 'VEG']
            cloud = cloud [vmin <= cloud['VEG']]
            cloud = cloud [cloud['VEG'] <= vmax]
            
        cloud.dropna(inplace = True)
    
    if cmin and cmax:
        if not (collections.Counter(cmin.keys()) == collections.Counter(cmax.keys())):
            print "Keys in cmin and cmax need to match. Aborting."
            return
        for key in cmin.keys():
            if key not in cloud.keys():
                print "Key {} not in the cloud. Abortin.".format(key)
                return
            cloud = cloud [cmin[key] <= cloud[key]]
            cloud = cloud [cloud[key] <= cmax[key]]

    cloud.reset_index(drop = True, inplace = True)

    return cloud

def display_stats(cloud, indices = None, low = 0.0008, high = 0.9992, output_file = None, dpi = 100, show = True, cmin = None, cmax = None, both = False):
    if not output_file and not show:
        return

    plt.close('all')
    plt.ioff()

    if indices:
        cloud = cloud[indices]
        cloud.reset_index(drop = True, inplace = True)
    else:
        indices = cloud.columns.values.tolist()


    cloud = filter_cloud(cloud, low, high, cmin, cmax, both)
        
#    fig, ax = plt.subplots()
    axes = scatter_matrix(cloud, alpha = 0.02, hist_kwds={'bins' : 50}, figsize = (1200/dpi, 800/dpi))
    fig = axes[0][0].figure
#    plt.ion()
#    fig.set_size_inches(600/fig.dpi, 400/fig.dpi)

    if output_file:
#        for ax in chain.from_iterable(zip(*axes)):
#            ax.set_rasterized(True)
        plt.savefig(output_file, format = os.path.splitext(os.path.basename(output_file))[-1][1:], dpi=dpi)

    if show:
        plt.show()
        fig.clf()
        plt.close(fig)
    
    plt.close('all')
    plt.ion()

def stats_pair(cloud, indices, \
               output_file = None, dpi = 400, show = True, \
               cmin = None, cmax = None, low = 0.0008, high = 0.9992, both = False, \
               levels = (0.03, 0.08, 0.15, 0.4, 0.6, 0.8), nbins = 50):
    if not output_file and not show:
        return

    plt.close('all')
    fig, ax = plt.subplots()
    plt.figure.figsize = (1200/dpi, 400/dpi)

    plt.ioff()

    if not len(indices) == 2:
        print "Indices should contain exactly two distinct index names. {} given. Aborting".format(len(indices))

    cloud = cloud[indices]
    cloud.reset_index(drop = True, inplace = True)

    cloud = filter_cloud(cloud, low, high, cmin, cmax, both)

#    if not cmin or not cmax or both:
#        quant = cloud.quantile([low, high])
#        cloud = cloud.apply (lambda x : x[(x > quant.loc[low, x.name]) & (x < quant.loc[high, x.name])], axis = 0)
#        cloud.dropna(inplace = True)
#    if cmin and cmax:    
#        cloud = cloud [cmin <= cloud[indices[0]]]
#        cloud = cloud [cloud[indices[0]] <= cmax]

#    cloud.dropna(inplace = True)

    H, xedges, yedges = numpy.histogram2d(cloud[indices[0]], cloud[indices[1]], bins = [nbins, nbins], normed = True)
    H = numpy.rot90(H)
    H = numpy.flipud(H)
    extent = [xedges[0], xedges[-1], yedges[0], yedges[-1]]
    
    print "max {}, min {}".format(numpy.amax(H), numpy.amin(H))
    print "count of points {} size of bin {}".format(cloud[indices[0]].size, abs(extent[0] - extent[1])*abs(extent[2] - extent[3])/(nbins*nbins))
    bin_area = abs(extent[0] - extent[1])*abs(extent[2] - extent[3])/(nbins*nbins)

    colors = ['#ff0000ff', '#aa5511ff', '#dd6622ff', '#ffda97ff', '#998822ff', '#779911ff']

    density = ax.imshow(H, interpolation = 'bilinear', origin = 'lower', cmap = 'hot', extent = extent, aspect = 'auto', alpha = 0.9)
    ax.autoscale(False)

    ax.set_xlabel(indices[0])
    ax.set_ylabel(indices[1])

    contours = ax.contour(gaussian_filter(H, 1.2), levels = levels, origin = 'lower', linewidths = 2.2, extent = extent, alpha = 1.0, colors = colors)
    for c in contours.collections:
        c.set_linestyle("solid")
    ax.clabel(contours, inline = 1, fontsize = 11, fmt = '%3.2f')
    ccolorbar = plt.colorbar(contours, shrink = 1.0, extend = 'both')
    dcolorbar = plt.colorbar(density, orientation = 'horizontal')

    l, b, w, h = density.axes.get_position().bounds
    ll, bb, ww, hh = ccolorbar.ax.get_position().bounds
    ccolorbar.ax.set_position([ll, b, ww*1.2, h*1.0])

    if output_file:
        plt.savefig(output_file, format = os.path.splitext(os.path.basename(output_file))[-1][1:], dpi=dpi)

    if show:
        plt.show() # can't invoke "event" command: application has been destroyed while executing
        fig.clf()
        plt.cla()
        plt.close()
    plt.close('all')
    plt.ion()

def display_index_cloud(cloud, index, low = 0.005, high = 0.995, output_file = None, show = True, invert = False, mmin = None, mmax = None, density = 5):
    if not output_file and not show:
        return
    cloud = cloud[numpy.abs(cloud.z - cloud.z.mean()) <= 3*cloud.z.std()]
    cloud.reset_index(drop = True, inplace = True)

    fig = mlab.figure('IndexCloud', size = (1000, 700))
    fig.scene.disable_render = True
    mlab.figure(figure = fig, bgcolor=(1,1,1), fgcolor=(0,0,0))

    if not mmin or not mmax:
        quant = cloud.quantile([low, high])
        vmin = quant[index][low]
        vmax = quant[index][high]
    else:
        vmin = mmin
        vmax = mmax

    if invert:
        cloud.loc[:, index] *= -1;
        vmin, vmax = vmax, vmin
    points = mlab.points3d(cloud['x'], cloud['y'], cloud['z'], cloud[index], figure = fig, mode='sphere', scale_mode = 'none', scale_factor = 0.02, mask_points = density, colormap = 'hot', vmin = vmin, vmax = vmax)

    axes = mlab.axes(points, color = (0.9, 0.9, 0.9), xlabel = '', ylabel = '', zlabel = 'height')
    axes.axes.property.line_width = 4
    axes.axes.font_factor = 1
    axes.axes.axis_label_text_property.font_family = 'times'
    axes.axes.axis_label_text_property.bold = False
    axes.axes.axis_title_text_property.font_family = 'times'
    axes.axes.axis_title_text_property.bold = False
   
    colorbar = points.parent.scalar_lut_manager.scalar_bar_widget
    colorbar_parent = points.parent.scalar_lut_manager
    position = [ [0.9, 0.2], [0.08, 0.75] ]
    colorbar.scalar_bar_representation.position = position[0]
    colorbar.scalar_bar_representation.position2 = position[1]
    colorbar.scalar_bar_representation.orientation = 90
    colorbar.resizable = False
    colorbar.repositionable = False
    colorbar.enabled = True
    colorbar_parent.title_text_property.font_family = 'times'
    colorbar_parent.title_text_property.bold = False
    colorbar_parent.label_text_property.font_family = 'times'
    colorbar_parent.label_text_property.bold = False
    colorbar_parent.data_name = ''

    x = position[0][0]
    y = position[0][1] + position[1][1] - 0.07

    colorbar_title = mlab.text(x,y, index)
    colorbar_title.property.bold = False
    colorbar_title.property.italic = True
    colorbar_title.property.font_family = 'times'
    colorbar_title.property.orientation = 0
    colorbar_title.width = 0.05

    fig.scene.disable_render = False

    if output_file:
        mlab.savefig(output_file, figure=fig, magnification=1)

    if show:
        mlab.show()
        mlab.clf(fig)
#        mlab.close()

def display_color_cloud(cloud, output_file = None, show = True, density = 5):
    if not output_file and not show:
        return
    cloud = cloud[numpy.abs(cloud.z - cloud.z.mean()) <= 3*cloud.z.std()]
    cloud.reset_index(drop = True, inplace = True)

    scalars = map(common.rgb_to_scalar, zip(cloud.r, cloud.g, cloud.b))

    fig = mlab.figure('ColorCloud', size = (810, 700), bgcolor = (1,1,1), fgcolor=(0,0,0))
    fig.scene.disable_render = True
#    mlab.figure(figure = fig, bgcolor=(1,1,1), fgcolor=(0,0,0))
    points = mlab.points3d(cloud['x'], cloud['y'], cloud['z'], scalars, figure = fig, mode='sphere', scale_mode = 'none', scale_factor = 0.02, mask_points = density)

    points.glyph.color_mode = 'color_by_scalar'
    points.module_manager.scalar_lut_manager.lut._vtk_obj.SetTableRange(0, lut_rgb.shape[0])
    points.module_manager.scalar_lut_manager.lut.number_of_colors = lut_rgb.shape[0]
    points.module_manager.scalar_lut_manager.lut.table = lut_rgb

    axes = mlab.axes(points, color = (0.9, 0.9, 0.9), xlabel = '', ylabel = '', zlabel = 'height', line_width = 4.0)
    axes.axes.font_factor = 1
    axes.axes.property.line_width = 4.0
    axes.axes.axis_label_text_property.font_family = 'times'
    axes.axes.axis_label_text_property.bold = False
    axes.axes.axis_title_text_property.font_family = 'times'
    axes.axes.axis_title_text_property.bold = False

    fig.scene.disable_render = False

    if output_file:
        mlab.savefig(output_file, figure=fig, magnification=1)

    if show:
        mlab.show()
        mlab.clf(fig)
        #mlab.close()



