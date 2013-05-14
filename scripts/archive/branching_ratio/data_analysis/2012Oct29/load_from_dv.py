import numpy as np

path = '/home/lattice/data/Experiments.dir/BranchingRatio.dir/2012Oct29.dir/2139_29.dir/'
timetag_file = '00001 - Timetags 2012Oct29_2139_29.csv'

fname = path + timetag_file
np_save = timetag_file[:-4]
print 'LOADING'
data = np.loadtxt(fname, delimiter=',')
print 'SAVING'
np.save(np_save, data)
print 'DONE'