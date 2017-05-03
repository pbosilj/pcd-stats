#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import cv2
import numpy as np
from matplotlib import pyplot as plt


import argparse

def main():

    ap = argparse.ArgumentParser(description = "Produce a histogram of the image (converted to grayscale if needed).")

    ap.add_argument("-i", "--image", required = True, help = "Path to the file containing the results of Otsu's thresholding for an image sequence.")
    ap.add_argument("-min", required = False, help = "Ignore all grayscale values in the image that are smaller than min.", default = '0')
    ap.add_argument("-max", required = False, help = "Ignore all grayscale values in the image that are larger or equal to max", default = '256')

    args = vars(ap.parse_args())

    gray_img = cv2.imread(args['image'], cv2.IMREAD_GRAYSCALE)

    hist = cv2.calcHist([gray_img],[0],None,[256],[0,256])
    plt.hist(gray_img.ravel(),bins = int(args['max'])-int(args['min']),range = [int(args['min']),int(args['max'])])
    plt.title('Histogram for gray scale picture')
    plt.show()

if __name__ == "__main__":
    main()
