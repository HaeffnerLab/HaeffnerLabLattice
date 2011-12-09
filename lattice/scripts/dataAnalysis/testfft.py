import labrad
import os
import numpy

cxn = labrad.connect()
dp = cxn.dataprocessor()

dp.set_inputs('timeResolvedFFT',[('uncompressedArrByteLength',27049),('resolution',5*10**-9)])
dp.new_process('timeResolvedFFT')

directory = 'C:\\Python26\\Lib\\idlelib\\__data__\\rawdata\\EnergyTransportv2\\2011Nov10_2241_33'
os.chdir(directory)
files = os.listdir(os.getcwd())
files.sort()

for file in files:
    print file
    f1 = numpy.load(file)
    data = f1['arr_0']
    print numpy.shape(data)
    info = f1['arr_1']
    #dp.process_new_data('timeResolvedFFT', data)