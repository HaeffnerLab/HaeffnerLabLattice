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

#change directory
directory = 'C:\\Python26\\Lib\\idlelib\\__data__\\rawdata\\localheatinglinescan\\WedSep141703242011'
os.chdir(directory)
files = os.listdir(os.getcwd())
files.sort()

dict = {}
#load file into a dict structure by frequency for easy access
files.remove('processed')
for file in files:
    print file
    [freq,trace] = file.strip('freq.npz').split('trace')
    if freq not in dict.keys(): 
        dict[freq] = [file] #create
    else:
        dict[freq].append(file)
    
keys = dict.keys()
keys.sort()

figure = pyplot.figure()
figure.clf()

t = time.time()
dp.set_inputs('timeResolvedBinning',[('timelength',0.125),('resolution',5.*10**-9),('bintime',0.5*10**-6)])

for item,key in enumerate(keys[::3]): #::3
    print 'processing freq {}'.format(key)
    dp.new_process('timeResolvedBinning')
    for file in dict[key]:
        print file
        fl = numpy.load(file)
        data = fl['arr_0']
        info = fl['arr_1']
        fl.close()
        dp.process_new_data('timeResolvedBinning',data)  
    binned = dp.get_result('timeResolvedBinning').asarray
    x = 1 - float(item) / len(keys[::3])
    pyplot.plot(binned[:,0],binned[:,1], label='Freq {} MHz'.format(key), color = cm.jet(x))

figure.suptitle('WedSep141703242011')
pyplot.xlabel('Time (sec)')
pyplot.ylabel('Counts, Arb')
pyplot.legend()
print 'DONE'
print time.time() - t
pyplot.show()
