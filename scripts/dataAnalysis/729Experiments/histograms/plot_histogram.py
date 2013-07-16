import labrad
from matplotlib import pyplot
#get access to servers
cxn = labrad.connect()
dv = cxn.data_vault

directory = ['','Experiments','Excitation729','2013Jun28','1844_23']
filename = '00001 - Readout 2013Jun28_1844_23'
#change directory

figure = pyplot.figure()

dv.cd(directory)
dv.open(filename)
data = dv.get().asarray
readout_counts = data[:,1]
n, bins, patches = pyplot.hist(readout_counts, 30, histtype='stepfilled')


pyplot.vlines(20, 0, 1000, color = 'red', linewidth = 5)
pyplot.xlabel( 'Collected Counts', fontsize = 60)
pyplot.ylabel('Occurence', fontsize = 60)
pyplot.tick_params('both', labelsize = 40)
pyplot.show()
