#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import numpy as np
import matplotlib

import argparse

def main():

    ap = argparse.ArgumentParser(description = "Display the histogram of thresholds for an image sequence contained in a text file.")

    ap.add_argument("-i", "--input", required = True, help = "Path to the file containing the results of Otsu's thresholding for an image sequence.")

    args = vars(ap.parse_args())

    f= np.loadtxt(args["input"], unpack='False')

    bins = np.linspace(0, 255, 256)

    plt.hist(f, bins, histtype='step', fill = True, rwidth=1)
    plt.ylabel('Threshold')
    plt.xlabel('Number of images')
    plt.title("Distribution of Otsu's threshold")
    plt.legend()
    plt.show()

if __name__ == "__main__":
    main()
