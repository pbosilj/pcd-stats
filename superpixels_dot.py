#!/usr/local/bin/python
# -*- coding: utf-8 -*-

# calculates the drop-out thresholds for all the superpixels according to a given model

import numpy

def superpixels_histograms(image, superpixels):
    num_sp = len(numpy.unique(superpixels))    
    hist = [[0]*256 for _ in xrange(num_sp)]
    counter = 0
    for (seg_val, px_val) in zip(numpy.nditer(superpixels, order = 'C'), numpy.nditer(image, order = 'C')):
        hist[int(seg_val)][int(px_val)] += 1
        counter += 1
    return hist

def k_percent_dot(histograms, k = 0.7, invert = False):
    thresholds = []
    for hist in histograms:
        hist_sum = sum(hist)

        if not invert:
            iterRange =  xrange(1, 256)
            cum_sum = numpy.cumsum(hist)
        else:
            iterRange = xrange(254, -1, -1)
            cum_sum = numpy.cumsum(hist[::-1])[::-1]
        for i in iterRange:
            if not invert:
                cur_sum = cum_sum[i-1]
            else:
                cur_sum = cum_sum[i+1]
            if float(cur_sum) / hist_sum > (1 - k):
                thresholds.append(i)
                break
    return thresholds

def average_dot(histograms, invert = False):
    thresholds = []
    for hist in histograms:
        hist_sum = sum(hist)
        sum_weighted = 0
        for i in xrange(1, 256):
            sum_weighted += i*hist[i]
        thresholds.append(sum_weighted/hist_sum)
    return thresholds

def median_dot(histograms, invert = False):
    thresholds = []
    superpixel = 0
    for hist in histograms:
        superpixel += 1
        hist_sum = sum(hist)
        cum_sum = numpy.cumsum(hist)
        for i in xrange(0, 256):
            if cum_sum[i]*2 > hist_sum:
                thresholds.append(i)
                break
            elif cum_sum[i]*2 == hist_sum:
                for j in xrange(i+1, 256):
                    if hist[j] > 0:
                        thresholds.append((i+j)/2)                
                        break
                break
    return thresholds

def dot_sort(single_dot, invert = False):
    dot_sorted = zip(single_dot, range(len(single_dot)))
    dot_sorted.sort()
    if invert:
        dot_sorted.reverse()
    return dot_sorted

def all_percent_dot(histograms, invert = False):
    thresholds = []
    for hist, sp in zip(histograms, range(len(histograms))):
        hist_sum = sum(hist)

        if not invert:
            iterRange =  xrange(1, 256)
            cum_sum = numpy.cumsum(hist)
        else:
            iterRange = xrange(254, -1, -1)
            cum_sum = numpy.cumsum(hist[::-1])[::-1]

        
        for i in iterRange:
            if i != iterRange[0]:
                prev_sum = cur_sum
            if not invert:
                cur_sum = cum_sum[i-1]
            else:
                cur_sum = cum_sum[i+1]
            if i != iterRange[0] and prev_sum != cur_sum:
                thresholds.append((1-float(prev_sum)/hist_sum, i, sp))
    return thresholds

