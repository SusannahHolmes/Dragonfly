#!/usr/bin/env python

'''
Convert CXI files as generated by the condor simulation package.

Needs:
    <condor_fname> - Path to condor output CXI file

Produces:
    EMC file with all the content of the condor CXI file
'''

import os
import numpy as np
import h5py
import sys
import logging
#Add utils directory to pythonpath
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from py_src import py_utils
from py_src import writeemc
from py_src import read_config

if __name__ == '__main__':
    logging.basicConfig(filename='recon.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    parser      = py_utils.my_argparser(description='condortoemc')
    parser.add_argument('condor_fname', help='Condor CXI file to convert to emc format')
    parser.add_argument('-o', '--output', help='Output folder, read from config file by default', type=str, default=None) 
    parser.add_argument('-l', '--list', help='condor_fname is list of condor CXI files rather than a single one', action='store_true', default=False)
    args        = parser.special_parse_args()

    logging.info('Starting condortoemc...')
    logging.info(' '.join(sys.argv))
    print args.config_file
    pm          = read_config.get_detector_config(args.config_file, show=args.vb)
    if args.output is None:
        output_folder = read_config.get_filename(args.config_file, 'emc', 'output_folder')
    else:
        output_folder = args.output

    if not os.path.isfile(args.condor_fname):
        print 'Data file %s not found. Exiting.' % args.condor_fname
        logging.error('Data file %s not found. Exiting.' % args.condor_fname)
        sys.exit()

    if args.list:
        logging.info('Reading file names in list %s' % args.condor_fname)
        with open(args.condor_fname, 'r') as f:
            flist = [fname.rstrip() for fname in f.readlines()]
        logging.info
    else:
        flist = [args.condor_fname]

    # Read meta information from condor CXI file
    with h5py.File(flist[0], 'r') as f:
        wavelength = f['source/wavelength'][...]
        nx = f['detector/nx'][0]
        ny = f['detector/ny'][0]
        
    emcwriter = writeemc.EMC_writer('%s/%s.emc' % (output_folder, os.path.splitext(os.path.basename(args.condor_fname))[0]), nx*ny)

    for fname in flist:
        f = h5py.File(fname, 'r')
        dset = f['entry_1/data_1/data']
        mask = f['entry_1/data_1/mask']
        num_frames = dset.shape[0]
        if not args.list:
            logging.info('Converting %d frames in %s' % (num_frames, args.condor_fname))

        for i in range(num_frames):
            photons = dset[i] * (~(mask[i]==512))
            photons[photons<0] = 0
            emcwriter.write_frame(photons.flatten())
            if not args.list:
                sys.stderr.write('\rFinished %d/%d' % (i+1, num_frames))
        f.close()

    if not args.list:
        sys.stderr.write('\n')
    emcwriter.finish_write()
