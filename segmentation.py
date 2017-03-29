from __future__ import print_function

import matplotlib.pyplot as plt
import numpy

from skimage.data import astronaut
from skimage.color import rgb2gray
from skimage.filters import sobel
from skimage.segmentation import felzenszwalb, slic, quickshift
from skimage.morphology import watershed
from skimage.segmentation import mark_boundaries
from skimage.util import img_as_float
from skimage.util import img_as_ubyte
from skimage import io

import argparse


def superpixel_histograms(image, superpixels):
    num_sp = len(numpy.unique(superpixels))    
    hist = [[0]*256 for _ in xrange(num_sp)]
    counter = 0
    for (seg_val, px_val) in zip(numpy.nditer(superpixels, order = 'C'), numpy.nditer(image, order = 'C')):
        hist[int(seg_val)][int(px_val)] += 1
        counter += 1
    return hist

def drop_out_thresholds(histograms, k = 0.7):
    thresholds = []
    for hist in histograms:
        hist_sum = sum(hist)
        cum_sum = numpy.cumsum(hist)
        for i in xrange(1, 255):
            if float(cum_sum[i]) / hist_sum >= (1 - k):
                thresholds.append(i)
                break
    return thresholds

def otsu_superpixel(image, superpixels, k = 0.7):
    histograms = superpixel_histograms(image, superpixels)
    dot = drop_out_thresholds(histograms, k)
    dot_sorted = zip(dot, range(len(dot)))
    dot_sorted.sort()

    sum_all = 0
    
    for hist in histograms:
        for i in xrange(1, 255):
            sum_all += i*hist[i]

    wB = 0
    sumB = 0

    var_max = 0
    threshold = 0

    current_superpixel = 0
    for thresh in xrange(0, 255):
        while current_superpixel < len(dot_sorted) and dot_sorted[current_superpixel][0] == thresh:
            wB += sum(histograms[dot_sorted[current_superpixel][1]])
            for i in xrange(1, 255):
                sumB += i*histograms[dot_sorted[current_superpixel][1]][i]
            current_superpixel += 1
        if wB == 0:
            continue
        wF = image.shape[0] * image.shape[1] - wB
        if wF == 0:
            break

        mB = sumB / wB
        mF = (sum_all - sumB) / wF
        
        var_between = float(wB) * float(wF) * ((mB - mF)**2)

        if var_between > var_max:
            var_max = var_between
            threshold = thresh

    accepted = []
    current_superpixel = len(dot_sorted)-1

    while current_superpixel >= 0 and dot_sorted[current_superpixel][0] > threshold:       
        accepted.append(dot_sorted[current_superpixel][1])
        current_superpixel -= 1

    
    print("Accepted {} out of {} superpixels".format(len(accepted), len(hist)))
    
    mask = numpy.zeros(image.shape[:2], dtype = "uint8")
#    print(image.shape[0] * image.shape[1])
#    for i in xrange(image.shape[0]):
#        for j in xrange(image.shape[1]):
#            if (counter % 10000) == 0:
#                print(counter)
#            counter += 1
#            if superpixels[i][j] in accepted:
#                mask[i][j] = 255

#    for value in accepted:
#        mask[superpixels == value] = 255
    mask[numpy.in1d(superpixels, accepted).reshape(mask.shape)] = 255
#    truth_mask = [ [ label in accepted for label in sp_row ] for sp_row in superpixels if sp_row.any() in accepted]
#    mask[truth_mask] = 255
#    mask[(superpixels in accepted).all()] = 255
#    for (mask_val, sp_num) in zip(numpy.nditer(mask, order = 'C', op_flags = ['readwrite']), numpy.nditer(superpixels, order = 'C')):
#        counter = counter+1
#        if sp_num in accepted:
#            mask_val[...] = 255

    return threshold, mask


# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required = True, help = "Path to the image")
args = vars(ap.parse_args())
 
# load the image and convert it to a floating point data type
img = img_as_float(io.imread(args["image"]))

print("Image input")

#img = img_as_float(astronaut()[::2, ::2])

import color_index
from functools import partial

from skimage import exposure

img_CIVE = numpy.apply_along_axis(partial(color_index.CIVE, normalize = False), 2, img)
img_CIVE_norm = exposure.rescale_intensity(img_CIVE, in_range = (img_CIVE.min(), img_CIVE.max()))

print(img_CIVE_norm.min())
print(img_CIVE_norm.max())

print("Image CIVE calculated")

segments_slic = slic(img_CIVE_norm, n_segments=35000, sigma = 0, convert2lab=False, compactness=0.05)

print("SLIC superpixels calculated")

#exit()

import cv2

ret,thr =cv2.threshold(img_as_ubyte(img_CIVE_norm),0,255,cv2.THRESH_OTSU)

print("Otsu's threshold calculated for CIVE image: {}".format(ret))

if 1:
    for k in numpy.linspace(0.2, 0.8, endpoint = True, num = 7):
        spret, spthr = otsu_superpixel(img_as_ubyte(img_CIVE_norm), segments_slic, k = k)
        print("Otsu's on Slick for acceptance percentage {} is {}".format(k, spret))
        fig, ax = plt.subplots(2,2, figsize=(10,10), sharex=True, sharey=True, subplot_kw={'adjustable':'box-forced'})
        ax[0,0].imshow(mark_boundaries(img_CIVE_norm, segments_slic))
        ax[0,0].set_title('SLIC on CIVE')
        ax[0,1].imshow(img)
        ax[0,1].set_title('Original')
        ax[1,0].imshow(thr, cmap = 'gray')
        ax[1,0].set_title("Otsu's threshold")
        #ax[1,1].imshow(thr_sp, cmap = 'gray')
        ax[1,1].imshow(spthr, cmap = 'gray')
        ax[1,1].set_title("Otsu's threshold on SLICK")

        for a in ax.ravel():
            a.set_axis_off()

        plt.tight_layout()
        plt.show()


exit()

seg_sizes = {}
seg_fullness = {}

thr_sp = numpy.copy(img)

for thr_perc in (1.0, 1.3, 1.5):
    thr_sp = numpy.copy(img)
    for full_perc in (0.6, 0.7, 0.8):
        for (seg_val, CIVE_val) in zip(numpy.nditer(segments_slic, order = 'C'), numpy.nditer(img_CIVE_norm, order = 'C')):
            seg_sizes[int(seg_val)] = seg_sizes.get(int(seg_val), 0) + 1
            if CIVE_val <= (float(ret)*thr_perc/255):
                seg_fullness[int(seg_val)] = seg_fullness.get(int(seg_val), 0) + 1

        for (seg_val, CIVE_val, out_r, out_g, out_b) in zip(numpy.nditer(segments_slic, order = 'C'), numpy.nditer(img_CIVE_norm, order = 'C'), numpy.nditer(thr_sp[...,0], order = 'C', op_flags = ['readwrite']), numpy.nditer(thr_sp[...,1], order = 'C', op_flags = ['readwrite']), numpy.nditer(thr_sp[...,2], order = 'C', op_flags = ['readwrite'])):
            if ( float(seg_fullness.get(int(seg_val), 0) ) / seg_sizes.get(int(seg_val), 0) ) >= full_perc:
                out_r[...] = 0
                out_g[...] = 0
                out_b[...] = 0

        print("CIVE on Superpixel, threshold {} coverage {} calculated.".format(thr_perc*ret, full_perc))


        fig, ax = plt.subplots(2,2, figsize=(10,10), sharex=True, sharey=True, subplot_kw={'adjustable':'box-forced'})
        ax[0,0].imshow(mark_boundaries(img_CIVE_norm, segments_slic))
        ax[0,0].set_title('SLIC on CIVE')
        ax[0,1].imshow(img)
        ax[0,1].set_title('Original')
        ax[1,0].imshow(thr, cmap = 'gray')
        ax[1,0].set_title("Otsu's threshold")
        ax[1,1].imshow(thr_sp, cmap = 'gray')
        ax[1,1].set_title('Threshold on SLICK')

        for a in ax.ravel():
            a.set_axis_off()

        plt.tight_layout()
        plt.show()

#fig = plt.figure("Superpixels")
#ax = fig.add_subplot(1,1,1)
#ax.imshow(img_CIVE_norm, cmap = 'gray')
#plt.show()



exit()

segments_fz = felzenszwalb(img, scale=500, sigma=0.1, min_size = 50)
segments_slic = slic(img, n_segments = 10000, sigma = 1, convert2lab = True, compactness = 10)
segments_quick = quickshift(img, kernel_size=3, max_dist=6, ratio=0.4, convert2lab = True)

#gradient = sobel(rgb2gray(img))
#segments_watershed = watershed(gradient, markers=250, compactness=0.001)
#segments_watershed = watershed(gradient, markers=250)

print("Felzenszwalb number of segments: {}".format(len(np.unique(segments_fz))))
print('SLIC number of segments: {}'.format(len(np.unique(segments_slic))))
print('Quickshift number of segments: {}'.format(len(np.unique(segments_quick))))

fig, ax = plt.subplots(2, 2, figsize=(10, 10), sharex=True, sharey=True,
                       subplot_kw={'adjustable': 'box-forced'})

ax[0, 0].imshow(mark_boundaries(img, segments_fz))
ax[0, 0].set_title("Felzenszwalbs's method")
ax[0, 1].imshow(mark_boundaries(img, segments_slic))
ax[0, 1].set_title('SLIC')
ax[1, 0].imshow(mark_boundaries(img, segments_quick))
ax[1, 0].set_title('Quickshift')
#ax[1, 1].imshow(mark_boundaries(img, segments_watershed))
ax[1, 1].imshow(img)
ax[1, 1].set_title('Original')

for a in ax.ravel():
    a.set_axis_off()

plt.tight_layout()
plt.show()
