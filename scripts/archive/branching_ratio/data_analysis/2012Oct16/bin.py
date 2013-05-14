import numpy as np
import labrad

#get timatags from the npy file
timetag_file = '00001 - Timetags 2012Oct16_2036_59.npy'
data = np.load(timetag_file)
timetags = data[:,1]
#get information from data vault
cxn = labrad.connect()
dv = cxn.data_vault
dv.cd(['Experiments','BranchingRatio','2012Oct16','2036_59'])
dv.open(1)
#will get these from data vault parameters for future data
start_recording_timetags = 0.00516 
cycle_time = 80e-6
timetags = (timetags - start_recording_timetags) % cycle_time
bin_size = 10e-9
bin_edges = 1 + cycle_time / bin_size
bins = np.linspace(0,cycle_time, bin_edges)
hist = np.histogram(timetags, bins)[0]
#save the binned data
together = np.vstack((bins[:-1], hist)).transpose()
bin_filename = timetag_file[:-4] + '_binned'
np.save(bin_filename, together)
