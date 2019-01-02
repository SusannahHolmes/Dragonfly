#!/usr/bin/env python

'''Module to calculate and save powder sum of frames'''

from __future__ import print_function
import numpy as np
from py_src import py_utils
from py_src import read_config

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

    pm = read_config.get_detector_config(args.config_file, show=args.vb) # pylint: disable=C0103

    x, y = np.indices((pm['dets_x'], pm['dets_y']))
    x = x.flatten()
    y = y.flatten()
    powder = np.zeros((x.max()+1, y.max()+1))

    # For each emc file, read data and add to powder
    for photons_file in photons_list:
        # Read photon data
        with open(photons_file, 'rb') as fptr:
            num_data = np.fromfile(fptr, dtype='i4', count=1)[0]
            num_pix = np.fromfile(fptr, dtype='i4', count=1)[0]
            print(photons_file+ ': num_data = %d, num_pix = %d' % (num_data, num_pix))
            if num_pix != len(x):
                print('Detector and photons file dont agree on num_pix')
            fptr.seek(1024, 0)
            ones = np.fromfile(fptr, dtype='i4', count=num_data)
            multi = np.fromfile(fptr, dtype='i4', count=num_data)
            place_ones = np.fromfile(fptr, dtype='i4', count=ones.sum())
            place_multi = np.fromfile(fptr, dtype='i4', count=multi.sum())
            count_multi = np.fromfile(fptr, dtype='i4', count=multi.sum())

        # Place photons in powder array
        np.add.at(powder, (x[place_ones], y[place_ones]), 1)
        np.add.at(powder, (x[place_multi], y[place_multi]), count_multi)

    # Write float64 array to file
    powder.tofile('data/powder.bin')

if __name__ == "__main__":
    main()
