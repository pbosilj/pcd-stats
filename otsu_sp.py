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

from functools import partial

import argparse
import numpy

import sys

def ratioFloat (string):
    value = float(string)
    if value < 0 or value > 1:
        raise argparse.ArgumentTypeError('Value of a ration has to be between 0 and 1.')
    return value

class _HelpAction(argparse._HelpAction):

    def __call__(self, parser, namespace, values, option_string=None):
        parser.print_help()

        # retrieve subparsers from parser
        subparsers_actions = [
            action for action in parser._actions
            if isinstance(action, argparse._SubParsersAction)]
        # there will probably only be one subparser_action,
        # but better save than sorry
        print
        for subparsers_action in subparsers_actions:
            # get all subparsers and print help
            for choice, subparser in subparsers_action.choices.items():
                print("Positional argument '{}':".format(choice))
                print(subparser.format_help())

        parser.exit()

def set_default_subparser(self, name, args=None):
    """default subparser selection. Call after setup, just before parse_args()
    name: is the name of the subparser to call by default
    args: if set is the argument list handed to parse_args()

    , tested with 2.7, 3.2, 3.3, 3.4
    it works with 2.6 assuming argparse is installed
    """
    subparser_found = False
    existing_default = False
    for arg in sys.argv[1:]:
        if arg in ['-h', '--help']:  # global help if no subparser
            break
    else:
        for x in self._subparsers._actions:
            if not isinstance(x, argparse._SubParsersAction):
                continue
            for sp_name in x._name_parser_map.keys():
                if sp_name in sys.argv[1:]:
                    subparser_found = True
                if sp_name == name:
                    existing_default = True
        if not subparser_found:
            # insert default in first position, this implies no
            # global options without a sub_parsers specified
            if not existing_default:
                for x in self._subparsers._actions:
                    if not isinstance(x, argparse._SubParsersAction):
                        continue
                    x.add_parser(name)
                    break
            self.add_argument("--dummy-subparser-guard", action = "store_true")
            if args is None:
                sys.argv.insert(len(sys.argv), name)
            else:
                args.insert(len(args), name)

argparse.ArgumentParser.set_default_subparser = set_default_subparser

def main():

    # construct the argument parser and parse the arguments
    ap = argparse.ArgumentParser(add_help=False)

    ap.add_argument ('-h', '--help', action=_HelpAction, help='show this help message and exit')
#    ap.add_argument('--help', action=_HelpAction, help='help for help if you need some help')  # add custom help


    ap.add_argument("-d", "--display", required = False, help = "Display the results of Otsu's segmentation on superpixels. Optionally, compare with Otsu's segmentation on pixels.", nargs = "?", const = "single", choices = ["single", "compare", "full"])
    ap.add_argument("-i", "--image", required = True, nargs = '+', help = "Path to the image or images to be processed.")
    
    verbosity_group = ap.add_mutually_exclusive_group()    
    verbosity_group.add_argument("-v", "--verbose", required = False, help = "Increase output verbosity", action = "store_true")
    verbosity_group.add_argument("-s", "--silent", required = False, help = "Silent execution. Only one number per line for each image is output", action = "store_true")

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

        if not args['silent']:
            print("Input image {}.".format(image_path))

        img_CIVE = numpy.apply_along_axis(partial(color_index.CIVE, normalize = False), 2, img)
        img_CIVE_norm = exposure.rescale_intensity(img_CIVE, in_range = (img_CIVE.min(), img_CIVE.max()))

        if not args['silent']:
            print("Image CIVE calculated")

        segments_slic = slic(img_CIVE_norm, n_segments=35000, sigma = 0, convert2lab=False, compactness=0.05)

        if not args['silent']:
            print("SLIC superpixels calculated")

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

        spret, spthr = superpixels_otsu.otsu_superpixels_fixed_dot(img_as_ubyte(img_CIVE_norm), segments_slic, invert = True, dot_function = dot_function, verbose = args['verbose'])[:2]
        
        if not args['silent']:
            print("Otsu's segmentation on superpixels completed, with T={}".format(spthr))
        else:
            print("{}".format(spthr))

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

            fig.set_title("Otsu's thresholding results")


            if args["display"] == "compare" or args["display"] == "full":

                ax[stax].imshow(spret, cmap = 'gray')
                ax[stax].set_title("Otsu's threshold on SLICK")
               
                import cv2

                thr, ret =cv2.threshold(img_as_ubyte(img_CIVE_norm),0,255,cv2.THRESH_OTSU+cv2.THRESH_BINARY_INV)

                if args['verbose']:                
                    print("Otsu's threshold calculated for CIVE image: {}".format(thr))

                ax[tax].imshow(ret, cmap = 'gray')
                ax[tax].set_title("Otsu's threshold")
                
                if args["display"] == "full":
                    ax[1,0].imshow(img_CIVE_norm, cmap = 'gray')
                    ax[1,0].set_title('CIVE')
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
        if not args['silent']:
            print

if __name__ == "__main__":
    main()
