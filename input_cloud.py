#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import pandas
import os
import glob
import subprocess as subproc
import sys
import common # for split_rgba

def read_cloud(path, filename, use_existing = False, cleanup_pcd = True, drop_a = True, drop_rgba = True): # read a single point could

    if filename.endswith((".xml", ".pcd")):
        filename = filename[0:-4]
    elif filename.endswith("_depth.pclzf"):
        filename = filename[0:-(len("_depth.pclzf"))]
    elif filename.endswith("_rgb.pclzf"):
        filename = filename[0:-(len("_rgb.pclzf"))]

    depth = os.path.join(path, filename+"_depth.pclzf")
    rgb = os.path.join(path, filename+"_rgb.pclzf")
    param = os.path.join(path, filename+".xml")
    output = os.path.join(path, filename+".pcd")

    if not use_existing or not os.path.isfile(output):
        if not os.path.isfile(depth) or not os.path.isfile(rgb) or not os.path.isfile(param):
            print("Insufficient input files to generate pcd. Needed: [NAME]_depth.pclzf, [NAME]_rgb.pclzf, [NAME].xml (with name = " + filename + ").")
            return None
        print("Generating pcd file " + output + ".")
        devnull = open(os.devnull, 'w')
        subproc.call(["pcl_pclzf2pcd", depth, rgb, param, output], stdout=devnull, stderr=devnull)
        subproc.call(["pcl_convert_pcd_ascii_binary", output, output, "0"], stdout=devnull, stderr=devnull)
    else:
        print("Using existing pcd file " + output + ".")

    cloud = pandas.read_csv(output, names = ['x', 'y', 'z', 'rgba'], skiprows = 11, sep = ' ')
    cloud.dropna(inplace = True)
    cloud = cloud[cloud.rgba != 4278190080]  
    cloud.loc[:, 'z'] *= -1
    cloud['r'], cloud['g'], cloud['b'], cloud['a'] = zip(*cloud['rgba'].map(common.scalar_to_rgba))
    if drop_rgba:
        cloud.drop('rgba', 1, inplace = True)
    if drop_a:
        cloud.drop('a', 1, inplace = True)
    cloud.reset_index(drop = True, inplace = True)

    if cleanup_pcd:
        print("Cleaning up pcd file " + output + ".")
        os.remove(output)

    return cloud

def read_clouds(path, filenames, use_existing = False, cleanup_pcd = True, drop_a = True, drop_rgba = True): # read multiple point clouds
    all_full_names = glob.glob(os.path.join(path,filenames))
    cloud = pandas.DataFrame()
    for filename in map(os.path.basename, all_full_names):
        if filename.endswith((".xml", ".pcd")):
            filename = filename[0:-4]
        elif filename.endswith("_depth.pclzf"):
            filename = filename[0:-(len("_depth.pclzf"))]
        elif filename.endswith("_rgb.pclzf"):
            filename = filename[0:-(len("_rgb.pclzf"))]
        cloud = cloud.append(read_cloud(path, filename, use_existing, cleanup_pcd, drop_a, drop_rgba))

    cloud.reset_index(drop = True, inplace = True)
    return cloud

def main():
    fullfile = sys.argv[1]
    path = os.path.dirname(fullfile)
    fileparts = os.path.splitext(os.path.basename(fullfile))
    filename = ''
    if fileparts[1] in ['.xml', '.pcd']:
        filename = fileparts[0]
    elif fileparts[0].split('_')[-1] in ["depth", "rgb"] and fileparts[1] == '.pclzf':
        filename = '_'.join(fileparts[0].split('_')[:-1])

    #path =  r'/media/petra/3D Weeding Datasets/Carrots Cockley Cley 20Oct2016/20161020T142815'
    #filename = "frame_20161020T142817.032019"

    if filename:
        cloud = read_cloud(path, filename, use_existing = True, cleanup_pcd = False)
        print(cloud.shape)
        print(cloud.describe())

if __name__ == "__main__":
    main()
