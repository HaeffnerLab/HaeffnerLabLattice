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
directory = 'C:\\Python26\\Lib\\idlelib\\__data__\\rawdata\\EnergyTransportv2\\2011Nov10_1729_37'
os.chdir(directory)
files = os.listdir(os.getcwd())
files.sort()

dp.set_inputs('timeResolvedBinning',[('timelength',0.125),('resolution',5.*10**-9),('bintime',5*10**-6)])

for file in files:
    print file
    f1 = numpy.load(file)
    data = f1['arr_0']
    info = f1['arr_1']
    dp.new_process('timeResolvedBinning')
    binned = dp.get_result('timeResolvedBinning').asarray
    dv.cd(['','Experiments','EnergyTransportv2','test'])
    dv.new('Counts',[('Time', 'sec')], [('PMT counts','Arb','Arb')] )
    dv.add(binned)

print 'Done'
