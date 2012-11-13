import labrad
import os
import numpy
import matplotlib
matplotlib.use('Qt4Agg')
from matplotlib import pyplot
from matplotlib import cm
import time

#get access to servers
cxn = labrad.connect()
dp = cxn.dataprocessor
dv = cxn.data_vault()

#change directory
directory = 'C:\\Python26\\Lib\\idlelib\\__data__\\rawdata\\EnergyTransportv2\\2011Nov10_2155_57'
os.chdir(directory)
files = os.listdir(os.getcwd())
files.sort()

dp.set_inputs('timeResolvedBinning',[('timelength',0.37),('resolution',5.*10**-9),('bintime',1*10**-6)])
dp.new_process('timeResolvedBinning')

for file in files:
    print file
    f1 = numpy.load(file)
    data = f1['arr_0']
    info = f1['arr_1']
    f1.close()
    dp.process_new_data('timeResolvedBinning',data)  
binned = dp.get_result('timeResolvedBinning').asarray
dv.cd(['','Experiments','EnergyTransportv2','test0'])
dv.new('Counts',[('Time', 'sec')], [('PMT counts','Arb','Arb')] )
dv.add(binned)

figure = pyplot.figure()
figure.suptitle('')
pyplot.xlabel('Time (sec)')
pyplot.ylabel('PMT counts, Arb')
pyplot.legend()
pyplot.show()

print 'Done'
