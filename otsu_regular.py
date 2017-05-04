#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import superpixels_dot
import superpixels_otsu
import color_index

import matplotlib.pyplot as plt

from skimage.color import rgb2gray
from skimage.segmentation import slic
from skimage.segmentation import mark_boundaries
from skimage.util import img_as_float
from skimage.util import img_as_ubyte
from skimage import io
from skimage import exposure

import os

from functools import partial

import argparse
import numpy

import sys

import argparse_help

def main():

    # construct the argument parser and parse the arguments
    ap = argparse.ArgumentParser(description = "Run Otsu's thresholding on an image or sequence of images using a selected color index.")

    #ap.add_argument ('-h', '--help', action=_HelpAction, help='show this help message and exit')

    ap.add_argument("-d", "--display", required = False, help = "Display the results of Otsu's segmentation. 'Full' display also displays the color index image and the original image.", nargs = "?", const = "single", choices = ["single", "full"])
    ap.add_argument("-s", "--save", required = False, help = "Save the output images to file", action = "store_true")
    ap.add_argument("-i", "--image", required = True, nargs = '+', help = "Path to the image or images to be processed.")

    ap.add_argument("-a", "--alpha", required = False, help = "Recency factor alpha, from range [0.0, 1.0]. Lower values mean longer system memory", default = "1.0", type=argparse_help.ratioFloat)

    ap.add_argument("-c", "--color-index", required = False, help = "Specify color index to use for obtaining the grayscale image to threshold", default = "CIVE", choices = ["CIVE", "nCIVE", "ExG", "ExR", "mExG", "nExG", "nExR", "nmExG", "VEG"])

    ap.add_argument("-v", "--verbose", required = False, help = "Increase output verbosity", action = "store_true")
    
    args = vars(ap.parse_args())

    thr_cur = 0
    thr_first = True

    for image_path in args["image"]:
        # load the image and convert it to a floating point data type
        img = img_as_float(io.imread(image_path))

        if args['verbose']:
            print("Input image {}.".format(image_path))

        normalize = False
        invert = False
        if args['color_index'][0] == 'n':
            normalize = True
        if args['color_index'][-4:] == 'CIVE':
            img_index = numpy.apply_along_axis(partial(color_index.CIVE, normalize = normalize), 2, img)
            invert = True
        elif args['color_index'][-3:] == 'ExG':
            img_index = numpy.apply_along_axis(partial(color_index.excess_green, normalize = normalize), 2, img)
        elif args['color_index'][-3:] == 'ExR':
            img_index = numpy.apply_along_axis(partial(color_index.excess_red, normalize = normalize), 2, img)
        elif args['color_index'][-4:] == 'mExR':
            img_index = numpy.apply_along_axis(partial(color_index.modified_excess_green, normalize = normalize), 2, img)
        elif args['color_index'][-3:] == 'VEG':
            img_index = numpy.apply_along_axis(partial(color_index.VEG, normalize = normalize), 2, img)

        image_gray_norm = exposure.rescale_intensity(img_index, in_range = (img_index.min(), img_index.max())) # get range -1 to 1 

        if args['verbose']:
            print("Image {} calculated.".format(args['color_index']))
            if args['save']:
                plt.imsave(os.path.splitext(image_path)[0]+"_"+args['color_index']+os.path.splitext(image_path)[-1], image_gray_norm, cmap = 'gray')

        import cv2

        if invert:
            thr, ret =cv2.threshold(img_as_ubyte(image_gray_norm),0,255,cv2.THRESH_OTSU+cv2.THRESH_BINARY_INV)
        else:
            thr, ret =cv2.threshold(img_as_ubyte(image_gray_norm),0,255,cv2.THRESH_OTSU+cv2.THRESH_BINARY)

        if not thr_first:
            thr_cur = int(thr_cur * (1-args['alpha']) + thr * args['alpha'])
        else:
            thr_cur = thr
            thr_first = False

        if args['verbose']:
            print("Otsu's segmentation completed, with T={}".format(int(thr)))

        if thr_cur != thr:
            if args['verbose'] and args['alpha'] < 1.0:
                print("Recency corrected with alpha={} to T={}".format(args['alpha'], int(thr_cur)))

            if invert:
                thr, ret =cv2.threshold(img_as_ubyte(image_gray_norm),thr_cur,255,cv2.THRESH_BINARY_INV)
            else:
                thr, ret =cv2.threshold(img_as_ubyte(image_gray_norm),thr_cur,255,cv2.THRESH_BINARY)


        if not args['verbose']:
            print("{}".format(int(thr)))
        
        if args['save']:
            plt.imsave(os.path.splitext(image_path)[0]+"_seg_"+args['color_index']+os.path.splitext(image_path)[-1], ret, cmap = 'gray')

        if args["display"]:
            if args["display"] == "single":
                fig, ax = plt.subplots(1,1, figsize=(5,5), sharex=True, sharey=True, subplot_kw={'adjustable':'box-forced'})
                ax.imshow(ret, cmap = 'gray')
                ax.set_title("Otsu's threshold")
                ax.set_axis_off()
            elif args["display"] == "full":
                fig, ax = plt.subplots(1,3, figsize=(15,5), sharex=True, sharey=True, subplot_kw={'adjustable':'box-forced'})
                ax[0].imshow(ret, cmap = 'gray')
                ax[0].set_title("Otsu's threshold")
                ax[1].imshow(image_gray_norm, cmap = 'gray')
                ax[1].set_title(args['color_index'])
                ax[2].imshow(img)
                ax[2].set_title('Original image')
                for a in ax.ravel():
                    a.set_axis_off()

            plt.tight_layout()
            plt.show()
        if args['verbose'] and image_path != args["image"][-1]:
            print

if __name__ == "__main__":
    main()
