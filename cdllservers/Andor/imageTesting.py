import numpy as np
from pylab import *


rawdata1 = np.loadtxt(r'C:\Users\lattice\Downloads\testandor\count-5ions-sample-dark\s60001.asc')
rawdata1 = rawdata1.transpose()
print rawdata1.shape
matshow(rawdata1)

rawdata2 = np.loadtxt(r'C:\Users\lattice\Downloads\testandor\count-5ions-sample-dark\s60002.asc')
rawdata2 = rawdata2.transpose()
matshow(rawdata2)

rawdata3 = np.loadtxt(r'C:\Users\lattice\Downloads\testandor\count-5ions-sample-dark\s60003.asc')
rawdata3 = rawdata3.transpose()
matshow(rawdata3)

show()