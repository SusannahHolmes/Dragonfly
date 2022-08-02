#!/usr/bin/env python
### must run powder.py first in order to get the powder output that is used as input in this python script


'''Module to calculate and save powder sum of frames'''

import numpy as np
import h5py
from matplotlib import pyplot as plt
from py_src.plot1d import *

d,radialprofile = plot1dxy()    
plt.plot(d,radialprofile)
#plt.xlim([d[int(stoprad)+1],d[-1]])
plt.show()
