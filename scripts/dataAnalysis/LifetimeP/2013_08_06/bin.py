import numpy as np
import labrad
from constants import constants as c

# throw_away = [74, 88, 89, 128, 176, 209, 212]
throw_away = []
#get timatags from the npy file
data = np.load(c.timetag_np_file)


iterations = data[:,0]
timetags = data[:,1]
to_delete = []
for index in throw_away:
    to_delete.extend( np.where(iterations == index)[0] )
timetags = np.delete(timetags, to_delete)


# iters, indices = np.unique(iterations, return_index = True)
# split = np.split(timetags, indices[1:])
# sums = np.array([tags.size for tags in split])
#finding out when we lost the ion
#print 'start'
#for i,s in enumerate(sums): print i,s
#print 'counts when the ion was lost'
#differences = np.ediff1d(sums)
#print sums[(differences.argmin() - 5):(differences.argmin() + 5)] 
#print differences.argmin()
# threshold = 2000.0

#no_ion_iter = np.where(sums < threshold)[0].min() + 1 #cut off at first point that's below the threshold
# no_ion_iter = 1001.0
#cut the iterations and timetags arrays to when we had the ion
# iterations = iterations[np.where(iterations < iters[no_ion_iter])]
# timetags = timetags[np.where(iterations < iters[no_ion_iter])]
# print 'Completed {} iterations before losing ion'.format(iterations.max() + 1)

cxn = labrad.connect()
dv = cxn.data_vault
dv.cd(c.datavault_dir)
dv.open(1)
# start_recording_timetags = dv.get_parameter('start_recording_timetags')
# cycle_time = dv.get_parameter('timetag_record_cycle')
start_recording_timetags = 0.001160 #doppler cooling , doppler cooling repump additional, sequence start, turn of all time
cycle_time = 0.000046
bin_size = 10e-9
print timetags.min()
print timetags.max()
timetags = (timetags - start_recording_timetags) % cycle_time
bin_edges = 1 + cycle_time / bin_size
print bin_edges
bins = np.linspace(0,cycle_time, bin_edges)
hist = np.histogram(timetags, bins)[0]
#save the binned data
together = np.vstack((bins[:-1], hist)).transpose()
bin_filename = c.bin_filename
np.save(bin_filename, together)
print 'DONE BINNING'