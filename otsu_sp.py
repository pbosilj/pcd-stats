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
import argparse_help
import numpy

import sys

argparse.ArgumentParser.set_default_subparser = argparse_help.set_default_subparser

def main():

    # construct the argument parser and parse the arguments
    ap = argparse.ArgumentParser(add_help=False, description = "Run Otsu's thresholding on a superpixel image or sequence of images using a selected color index.")

    ap.add_argument ('-h', '--help', action=argparse_help._HelpAction, help='show this help message and exit')
#    ap.add_argument('--help', action=_HelpAction, help='help for help if you need some help')  # add custom help


    ap.add_argument("-d", "--display", required = False, help = "Display the results of Otsu's segmentation on superpixels. Optionally, compare with Otsu's segmentation on pixels.", nargs = "?", const = "single", choices = ["single", "compare", "full"])
    ap.add_argument("-s", "--save", required = False, help = "Save the output images to file", action = "store_true")
    ap.add_argument("-i", "--image", required = True, nargs = '+', help = "Path to the image or images to be processed.")
    
    ap.add_argument("-c", "--color-index", required = False, help = "Specify color index to use for obtaining the grayscale image to threshold", default = "CIVE", choices = ["CIVE", "nCIVE", "ExG", "ExR", "mExG", "nExG", "nExR", "nmExG", "VEG"])

    verbosity_group = ap.add_mutually_exclusive_group()    
    verbosity_group.add_argument("-v", "--verbose", required = False, help = "Increase output verbosity", action = "store_true")
    verbosity_group.add_argument("-q", "--quiet", required = False, help = "Quiet execution. Only one number per line for each image is output.", action = "store_true")

    ap.add_argument("-m", "--model", required = False, help = "Select a model used for superpixel representation.", action = "store_true")
    subparsers = ap.add_subparsers(help="Model selection for the --model option. (Only used when -m is used)", dest='model_sel')   
    # average parser
    avg_parser = subparsers.add_parser('avg', help = "Use the average superpixel graylevel as superpixel model (Superpixel sp accepted for theshold T if avg(sp) > T).")
    # median parser
    med_parser = subparsers.add_parser('med', help = "Use the median superpixel graylevel as superpixel model (Superpixel sp accepted for theshold T if med(sp) > T).")
    # percentage parser
    perc_parser = subparsers.add_parser('perc', help = "Use the acceptance percentage as superpixel model (Superpixel sp is accepted for threshold T if the ratio of pixels p > T and total pixels in the region is greater than k).")
    perc_parser.add_argument("-k", help = "Defines the acceptance percentage for the percentage model. Values from [0.0, 1.0] accepted.", required = False, default = "0.7", type=ratioFloat)

    ap.set_default_subparser('no_model')

    args = vars(ap.parse_args())

    if args['model'] and args['model_sel'] == 'no_model':
        parser.error('A model needs to be provided {avg, med, perc} when --model is used.')
    if args['model_sel'] != 'no_model' and not args['model']:
        parser.error('A model is only accepted when --model option is provided.')

    for image_path in args["image"]:

        # load the image and convert it to a floating point data type
        img = img_as_float(io.imread(image_path))

        if not args['quiet']:
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

        #print("Min max {} {}".format(img_index.min(), img_index.max()))

        image_gray_norm = exposure.rescale_intensity(img_index, in_range = (img_index.min(), img_index.max())) # get range -1 to 1 

        if not args['quiet']:
            print("Image {} calculated.".format(args['color_index']))
            if args['save']:
                plt.imsave(os.path.splitext(image_path)[0]+"_"+args['color_index']+os.path.splitext(image_path)[-1], image_gray_norm, cmap = 'gray')

        segments_slic = slic(image_gray_norm, n_segments=35000, sigma = 0, convert2lab=False, compactness=0.05)

        if not args['quiet']:
            print("SLIC superpixels calculated.")

        if not args['model'] or args['model_sel'] == 'avg':
            dot_function = superpixels_dot.average_dot
            if args['verbose']:
                print("Using the average ('avg') model for superpixel acceptance.")
        elif args['model_sel'] == 'med':
            dot_function = superpixels_dot.median_dot
            if args['verbose']:
                print("Using the median ('med') model for superpixel acceptance.")
        elif args['model_sel'] == 'perc':
            dot_function = partial(superpixels_dot.k_percent_dot, k = args['k'])
            if args['verbose']:
                print("Using the acceptance percentage ('perc') model for superpixel acceptance.")

        spthr, spret = superpixels_otsu.otsu_superpixels_fixed_dot(img_as_ubyte(image_gray_norm), segments_slic, invert = invert, dot_function = dot_function, verbose = args['verbose'])[:2]
        
        if not args['quiet']:
            print("Otsu's segmentation on superpixels completed, with T={}".format(spthr))
        else:
            print("{}".format(spthr))

        if args['save']:
            plt.imsave(os.path.splitext(image_path)[0]+"_spseg_"+args['color_index']+os.path.splitext(image_path)[-1], spret, cmap = 'gray')

        if args["display"]:
            if args["display"] == "full":
                fig, ax = plt.subplots(2,2, figsize=(10,10), sharex=True, sharey=True, subplot_kw={'adjustable':'box-forced'})
                stax = (0,0)
                tax = (0,1)
            elif args["display"] == "single":
                fig, ax = plt.subplots(1,1, figsize=(5,5), sharex=True, sharey=True, subplot_kw={'adjustable':'box-forced'})
                stax = 0
            elif args["display"] == "compare":
                fig, ax = plt.subplots(1,2, figsize=(10,5), sharex=True, sharey=True, subplot_kw={'adjustable':'box-forced'})
                stax = 0
                tax = 1

            if args["display"] == "compare" or args["display"] == "full":

                ax[stax].imshow(spret, cmap = 'gray')
                ax[stax].set_title("Otsu's threshold on SLICK")
               
                import cv2

                if invert:
                    thr, ret =cv2.threshold(img_as_ubyte(image_gray_norm),0,255,cv2.THRESH_OTSU+cv2.THRESH_BINARY_INV)
                else:
                    thr, ret =cv2.threshold(img_as_ubyte(image_gray_norm),0,255,cv2.THRESH_OTSU+cv2.THRESH_BINARY)

                if args['verbose']:                
                    print("Otsu's threshold calculated for {} image: {}".format(args['color_index'], thr))

                if args['save']:
                    plt.imsave(os.path.splitext(image_path)[0]+"_seg_"+args['color_index']+os.path.splitext(image_path)[-1], ret, cmap = 'gray')


                ax[tax].imshow(ret, cmap = 'gray')
                ax[tax].set_title("Otsu's threshold")
                
                if args["display"] == "full":
                    ax[1,0].imshow(image_gray_norm, cmap = 'gray')
                    ax[1,0].set_title(args['color_index'])
                    ax[1,1].imshow(mark_boundaries(img, segments_slic))
                    ax[1,1].set_title('SLIC on Original')
                for a in ax.ravel():
                    a.set_axis_off()
            else:
                ax.imshow(spret, cmap = 'gray')
                ax.set_title("Otsu's threshold on SLICK")
                ax.set_axis_off()        


            plt.tight_layout()
            plt.show()
        if not args['quiet'] and image_path != args["image"][-1]:
            print

if __name__ == "__main__":
    main()
