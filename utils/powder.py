#!/usr/bin/env python

'''Module to calculate and save powder sum of frames'''

from __future__ import print_function
import numpy as np
import h5py
from matplotlib import pyplot as plt
from py_src import py_utils
from py_src import read_config
from py_src import detector

def main():
    '''Generate virutal powder pattern by adding up all frames'''
    # Read detector and photons file from config
    parser = py_utils.MyArgparser(description="Generate virtual powder pattern")
    args = parser.special_parse_args()
    
    try:
        photons_list = [read_config.get_filename(args.config_file, 'emc', "in_photons_file")]
    except read_config.configparser.NoOptionError:
        with open(read_config.get_param(args.config_file, 'emc', "in_photons_list"), 'r') as fptr:
            photons_list = [line.rstrip() for line in fptr.readlines()]
    try:
        det_fname = read_config.get_filename(args.config_file, 'emc', 'in_detector_file')
    except:
        print('emc:::in_detector_file not found. Note that single detector file needed for powder sum')
        return
    
    det = detector.Detector(det_fname)
    powder = np.zeros(det.x.shape, dtype=np.int32)
    assem_powder = np.zeros(det.frame_shape, dtype=np.int32)
    
    #if photons input file is an .emc extension
    if str(photons_list[0]).split('.')[-1] == 'emc':
        # For each emc file, read data and add to powder
        for photons_file in photons_list:
            # Read photon data
            with open(photons_file, 'rb') as fptr:
                num_data = np.fromfile(fptr, dtype='i4', count=1)[0]
                num_pix = np.fromfile(fptr, dtype='i4', count=1)[0]
                print(photons_file+ ': num_data = %d, num_pix = %d' % (num_data, num_pix))
                if num_pix != len(powder):
                    print('Detector and photons file dont agree on num_pix')
                fptr.seek(1024, 0)
                ones = np.fromfile(fptr, dtype='i4', count=num_data)
                multi = np.fromfile(fptr, dtype='i4', count=num_data)
                place_ones = np.fromfile(fptr, dtype='i4', count=ones.sum())
                place_multi = np.fromfile(fptr, dtype='i4', count=multi.sum())
                count_multi = np.fromfile(fptr, dtype='i4', count=multi.sum())
    
    #if photons input file is an .h5 extension
    elif str(photons_list[0]).split('.')[-1] == 'h5':
        # Read data and add to make powder
        for photons_file in photons_list:
            # Read photon data
            with h5py.File(photons_file) as fptr:
                num_data = fptr['count_multi'].shape[0]
                num_pix = fptr['num_pix'][0]
                print(photons_file+ ': num_data = %d, num_pix = %d' % (num_data, num_pix))
                if num_pix != len(powder):
                    print('Detector and photons file dont agree on num_pix')
                place_ones = np.hstack(np.array(fptr['place_ones']))
                place_multi = np.hstack(np.array(fptr['place_multi']))
                count_multi = np.hstack(np.array(fptr['count_multi']))
    else:
        print('photons file type not supported')
            
    # Place photons in powder array
    np.add.at(powder, place_ones, 1)
    np.add.at(powder, place_multi, count_multi)
    np.add.at(assem_powder, (det.x[place_ones], det.y[place_ones]), 1)
    np.add.at(assem_powder, (det.x[place_multi], det.y[place_multi]), count_multi)
    # Write float64 array to file
    powder.tofile('data/powder.bin')
    np.savetxt('data/powder_%d_%d.csv'%det.frame_shape, assem_powder,delimiter=',')

if __name__ == "__main__":
    main()
