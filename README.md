# pcd-stats

# support functions and libraries (also for interactive work)
# describing different vegetation-directed color indices for rgb images
color_index.py 
common.py

# support for work and statistical analysis of the point clouds
input_cloud.py
process_cloud.py

# support functions for work with superpixels and Otsu's thresholding
superpixels_dot.py
superpixels_otsu.py

# -----------------------------------------------------------------------

# scripts for obtaining thresholding results on an image using Otsu's segmentation (directly on pixels, simplified treating superpixels as pixels, and implemented on superpixels)
otsu_regular.py
otsu_reduced_sp.py
otsu_sp.py

# Execution examples:

# Otsu's segmentation on pixels. Save generated images, process whole folder, recency 0.2 (0.8 history - 0.2 current), use CIVE index
~$ python -W ignore otsu_regular.py -s -i testing/carrots/*.png -a 0.2 -c CIVE > otsu_pixels_CIVE_a_0.2.txt 

# Otsu's segmentation treating superpixels as pixels (variance calculated using only 1 value per superpixel). Save images, verbose output, use CIVE index and median representation of superpixels
~$ python -W ignore otsu_reduced_sp.py -s -v -i testing/carrots/*_orig.png -c CIVE -m med > testing/otsu_sp_reduced_med_CIVE_carrots.txt

# Otsu's segmentation on superpixels (variance calculated using all pixels within a superpixel). Quiet output, run on three images, display the full comparison (with simple Otsu, the index image and the original image with superpixel overlay), use ExG index and average representation for superpixels
~$ python -W ignore otsu_sp.py -q -i testing/carrots/frame_20160915T125739.977576_orig.png testing/carrots/frame_20160915T125740.110574_orig.png testing/carrots/frame_20160915T125740.210576_orig.png -d full -c ExG -m avg

# Get help and argument explanation (all three scripts have the functionality)
~$ python otsu_sp.py --help

# -----------------------------------------------------------------------

# scripts for analysis of the thresholding results and images
hist.py
img_hist.py
timeseries.py

# Execution examples:

# Histogram of all threshold values for a sequence

~$ python -W ignore hist.py -i testing/otsu_sp_reduced_med_CIVE.txt

# Timeserieries of the threshold values 

~$ python -W ignore timeseries.py -i testing/otsu_sp_reduced_med_CIVE.txt

# Histogram of image values, between the graylevels of 2 and 130

~$ python -W ignore img_hist.py -i testing/ndvi2.png -min 2 -max 150

