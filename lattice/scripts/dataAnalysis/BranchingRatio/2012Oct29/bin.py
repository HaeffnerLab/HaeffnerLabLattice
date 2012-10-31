import numpy as np
import labrad

#get timatags from the npy file
timetag_file = '00001 - Timetags 2012Oct29_2139_29.npy'
data = np.load(timetag_file)
iterations = data[:,0]
timetags = data[:,1]
iters, indices = np.unique(iterations, return_index = True)
split = np.split(timetags, indices[1:])
#find when we lost the ion
threshold = 13000.0
sums = np.array([tags.size for tags in split])
no_ion_iter = np.where(sums > threshold)[0].max() + 1
#cut the iterations and timetags arrays to when we had the ion
iterations = iterations[np.where(iterations < iters[no_ion_iter])]
timetags = timetags[np.where(iterations < iters[no_ion_iter])]
print 'Completed {} iterations before losing ion'.format(iterations.max() + 1)

cxn = labrad.connect()
dv = cxn.data_vault
dv.cd(['Experiments','BranchingRatio','2012Oct29','2139_29'])
dv.open(1)
##will get these from data vault parameters for future data
start_recording_timetags = dv.get_parameter('start_recording_timetags')
cycle_time = dv.get_parameter('timetag_record_cycle')
bin_size = 10e-9
timetags = (timetags - start_recording_timetags) % cycle_time
bin_edges = 1 + cycle_time / bin_size
bins = np.linspace(0,cycle_time, bin_edges)
hist = np.histogram(timetags, bins)[0]
#save the binned data
together = np.vstack((bins[:-1], hist)).transpose()
bin_filename = timetag_file[:-4] + '_binned'
np.save(bin_filename, together)