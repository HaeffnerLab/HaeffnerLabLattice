import numpy as np

path = '/home/lattice/data/Experiments.dir/BranchingRatio.dir/2012Oct16.dir/2036_59.dir/'
timetag_file = '00001 - Timetags 2012Oct16_2036_59.csv'

#path = '/home/lattice/data/Experiments.dir/BranchingRatio.dir/2012Oct16.dir/1849_21.dir/'
#timetag_file = '00001 - Timetags 2012Oct16_1849_21.csv'

fname = path + timetag_file
np_save = timetag_file[:-4]
print 'LOADING'
data = np.loadtxt(fname, delimiter=',')
print 'SAVING'
np.save(np_save, data)
print 'DONE'