#!/usr/bin/env python
### must run powder_h5.py first in order to get the powder output that is used as input in this python script


'''Module to calculate and save powder sum of frames'''

from __future__ import print_function
import numpy as np
import h5py
from matplotlib import pyplot as plt
from py_src import py_utils
from py_src import read_config
from py_src import detector

def plot1dxy():
    # Read detector and photons file from config
    parser = py_utils.MyArgparser()
    args = parser.special_parse_args()

    #location of powder
    try:
        det_fname = read_config.get_filename(args.config_file, 'emc', 'in_detector_file')
    except:
        print('emc:::in_detector_file not found. Note that single detector file needed for powder sum')

    det = detector.Detector(det_fname)
    dataloc = 'data/powder_%d_%d.csv'%det.frame_shape
    data_array = np.genfromtxt(dataloc, delimiter=',')

    ##visualise powder image
    #plt.imshow(data_array, interpolation='nearest')
    #plt.show()

    #Get 1D plot
    try:
        detd = read_config.get_filename(args.config_file, 'parameters', 'detd') #in mm
        pixsize = read_config.get_filename(args.config_file, 'parameters', 'pixsize') #in mm
        lambd = read_config.get_filename(args.config_file, 'parameters', 'lambda') #in angstrom
        stoprad = read_config.get_filename(args.config_file, 'parameters', 'stoprad') #in pixels
    except:
        print('parameters not found in config.ini file')
    
    center = data_array.shape[0]/2 #assuming square detector
    y,x=np.indices((data_array.shape))
    r = np.sqrt((x-center)**2+(y-center)**2)
    r = r.astype(np.int)
    tbin = np.bincount(r.ravel(), data_array.ravel())
    nr = np.bincount(r.ravel())
    radialprofile = tbin / nr
    xrad_pix = range(len(nr))
    gamma = [np.arctan((i*float(pixsize))/float(detd)) for i in xrad_pix] #in degrees
    d = [float(lambd)/(2*np.sin(i/2)) for i in gamma] #in angstrom
    #plt.plot(d,radialprofile)
    #plt.xlim([d[int(stoprad)+1],d[-1]])
    #plt.show()
    return d, radialprofile
