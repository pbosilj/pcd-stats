#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import superpixels_dot # for dot_sorted
import numpy

from functools import partial

def otsu_core(image, histograms, dot, invert = False, verbose = False):
    dot_sorted = superpixels_dot.dot_sort(dot, invert)

#    sum_all = 0
    
    sum_all = sum([i*hist[i] for hist in histograms for i in xrange(1, 256)])

#    for hist in histograms:
#        for i in xrange(1, 256):
#            sum_all += i*hist[i]

    wB = 0
    sumB = 0
    var_max = 0

    current_superpixel = 0
    if not invert:
        iterRange = xrange(0, 256)
    else:
        iterRange = xrange(255, -1, -1)

    for thresh in iterRange:
        while current_superpixel < len(dot_sorted) and dot_sorted[current_superpixel][0] == thresh:
            wB += sum(histograms[dot_sorted[current_superpixel][1]])
            sumB += sum([i*histograms[dot_sorted[current_superpixel][1]][i] for i in xrange(1,256)])
#            for i in xrange(1, 256):
#                sumB += i*histograms[dot_sorted[current_superpixel][1]][i]
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

    if verbose:
        print("Otsu's thresholding for superpixels: best threshold={} for variance={}.".format(threshold, var_max))

    return var_max, threshold

def otsu_mask(superpixels, dot, threshold, invert = False, verbose = False):

    dot_sorted = superpixels_dot.dot_sort(dot, invert)

    accepted = []
    current_superpixel = len(dot_sorted)-1

    while current_superpixel >= 0 and ((invert == False and dot_sorted[current_superpixel][0] > threshold) or (invert == True and dot_sorted[current_superpixel][0] < threshold)):       
        accepted.append(dot_sorted[current_superpixel][1])
        current_superpixel -= 1

    if verbose:
        print("Accepted {} out of {} superpixels".format(len(accepted), len(dot_sorted)))

    mask = numpy.zeros(superpixels.shape[:2], dtype = "uint8")
    mask[numpy.in1d(superpixels, accepted).reshape(mask.shape)] = 255

    return mask

def otsu_superpixels_precentage(image, superpixels, invert = False, verbose = False):
    histograms = superpixels_dot.superpixels_histograms(image, superpixels)

    mult = 1
    if invert:
        mult = -1

    all_thr = sorted(superpixels_dot.all_precent_dot(histograms, invert), key = lambda t:(-t[0]*mult, mult*t[1])) # do I even need t[1] or is it unique

    if not invert: #check the initialization
        dot_cur = [1] * len(histograms)
    else:
        dot_cur = [254] * len(histograms)
    
    i = 0
    var_max = 0
    threshold = 0
    k_best = 0

    k_start = 0.2
    k_end = 0.8

    tests = 0
    while i < len(all_thr):
        k = all_thr[i][0]
        while i < len(all_thr) and all_thr[i][0] == k:
            dot_cur[all_thr[i][2]] = all_thr[i][1]
            i += 1
        if (k < k_start):
            continue
        if (k > k_end):
            break
        tests += 1
        var, thr = otsu_core(image, histograms, dot_cur, invert, verbose)
        if verbose:
            print("Test # {} with k={}, output var={}, thr={} (best var={} for thr={} at k={}).".format(tests, k, var, thr, var_max, threshold, k_best))
        if var > var_max:
            var_max = var
            threshold = thr
            k_best = k

    if verbose:
        print("Otsu for all k on superpixels found: best k={}, threshold={} (while doing {} tests)".format(k_best, threshold, tests))

    if not invert: #check the initialization like above
        dot_cur = [1] * len(histograms)
    else:
        dot_cur = [254] * len(histograms)
    i = 0
    while i < len(all_thr) and all_thr[i][0] != k:
        dot_cur[all_thr[i][2]] = all_thr[i][1]
        i += 1
    while i < len(all_thr) and all_thr[i][0] == k:
        dot_cur[all_thr[i][2]] = all_thr[i][1]
        i += 1

    mask = otsu_mask(superpixels, dot_cur, threshold, invert, verbose)

    return mask, threshold, k_best

def otsu_superpixels_fixed_dot(image, superpixels, invert = False, dot_function = partial(superpixels_dot.k_percent_dot, k = 0.7), verbose = False):        
    histograms = superpixels_dot.superpixels_histograms(image, superpixels)
#    dot = drop_out_thresholds(histograms, k, invert)  # or any other way to get drop-out-thresholds -> should maybe 
#    dot = median_thresholds(histograms, invert)
    dot = dot_function(histograms, invert = invert)

    var_max, threshold = otsu_core(image, histograms, dot, invert, verbose)
    mask = otsu_mask(superpixels, dot, threshold, invert, verbose)

    return mask, threshold

