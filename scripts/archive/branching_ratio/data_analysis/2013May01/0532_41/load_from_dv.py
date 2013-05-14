import numpy as np
from constants import constants as c

path = c.local_path
timetag_file = c.local_timetag_file

fname = path + timetag_file
np_save = timetag_file[:-4]
print 'LOADING'
data = np.loadtxt(fname, delimiter=',')
print 'SAVING'
np.save(np_save, data)
print 'DONE'