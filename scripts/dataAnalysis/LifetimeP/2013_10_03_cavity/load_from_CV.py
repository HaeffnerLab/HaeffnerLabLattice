import numpy as np

data = np.loadtxt('locked_data.CSV', delimiter=',')
print 'SAVING'
np.save('locked.npy', data)
print 'DONE'