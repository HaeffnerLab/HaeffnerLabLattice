import labrad
import numpy as np
#get access to servers
cxn = labrad.connect()
dv = cxn.data_vault
#prepare data
total_fft = np.zeros(5*10**7+1)
#change directory
#dataset = '1555_40' #slope
#dataset = '1553_55' #top of peak
#dataset = '1558_44' #ion oscllating axially
dataset = '1602_25' #ion oscillating radially

dv.cd(['','SimpleMeasurements','Timetags','2012Oct29',dataset])
dv.open(1)
data = dv.get().asarray
iterations = data[:,0]
timetags = data[:,1]
iters,indices =  np.unique(iterations, return_index=True)
split = np.split(timetags, indices[1:])
for i,tags in enumerate(split):
    print 'working on', i
    arrival_times = np.zeros(10**8)
    positions = np.array(tags / 10e-9,  dtype = np.uint)
    arrival_times[positions] = 1
    fft = np.abs(np.fft.rfft(arrival_times))
    total_fft+= fft
    del(fft)
    del(arrival_times)
    del(positions)
#plot the output
print 'saving'
np.save(dataset, total_fft)
print 'DONE'