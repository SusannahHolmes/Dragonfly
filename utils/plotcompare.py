#!/usr/bin/env python

from __future__ import print_function
import numpy as np
from matplotlib import pyplot as plt
from py_src import py_utils
from py_src import read_config
from py_src import detector
import sys
import os
import h5py
from py_src import plot1d

curr = os.getcwd()
firstdir = input("enter full directory location of first dataset to compare (eg. /home/Dragonfly/recon_0001/):")
os.chdir(firstdir)
d1, rad1 = plot1dxy()
seconddir = input("enter full directory location of second dataset to compare (eg. /home/Dragonfly/recon_0002/):")
os.chdir(seconddir)
d2, rad2 = plot1dxy()
os.chdir(curr)

plt.plot(d1,rad1)
plt.plot(d2,rad2)
plt.show()


