#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import numpy as np
import matplotlib

import argparse

def main():

    ap = argparse.ArgumentParser(description = "Display the evolution of thresholds for an image sequence contained in a text file.")

    ap.add_argument("-i", "--input", required = True, help = "Path to the file containing the results of Otsu's thresholding for an image sequence.")

    args = vars(ap.parse_args())

    y = np.loadtxt(args["input"], unpack='False')
    x = np.linspace(0, y.shape[0], y.shape[0]) 

    plt.plot(x,y)
    plt.ylim(ymax = 255, ymin = 0)
    plt.ylabel('Threshold')
    plt.xlabel('# image in sequence')
    plt.title("Evolution of Otsu's threshold")
    plt.legend()
    plt.show()

if __name__ == "__main__":
    main()
