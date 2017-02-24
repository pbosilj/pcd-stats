#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import input_cloud
import color_index
import process_cloud

from functools import partial

path =  r'.'
filename = "frame_20161020T142817.032019"
cloud = input_cloud.read_cloud(path, filename, use_existing = True, cleanup_pcd = False)

#filenames = "frame*"
#cloud = input_cloud.read_clouds(path, filenames, use_existing = True, cleanup_pcd = False)

#print(cloud.describe())

#cloud = process_cloud.add_index(cloud, partial(color_index.excess_green, normalize = False), 'ExG')
cloud = process_cloud.add_index(cloud, partial(color_index.CIVE, normalize = False), 'CIVE')

print("Displaying cloud:")
process_cloud.display_color_cloud(cloud)
print("Displaying height cloud:")
process_cloud.display_index_cloud(cloud, 'z')
print("Displaying index cloud:")
process_cloud.display_index_cloud(cloud, 'CIVE', invert = True)
print("Display stats:")
process_cloud.display_stats(cloud, ['CIVE', 'z'])
print("Display detailed:")
process_cloud.stats_pair(cloud, ['CIVE', 'z'])

print("Display multiple stats:")
cloud = process_cloud.add_index(cloud, partial(color_index.excess_green, normalize = False), 'ExG')
process_cloud.display_stats(cloud, ['CIVE', 'ExG', 'z'])

#print(color_index.excess_green(cloud.loc[0].copy(deep = True), normalize = True))
