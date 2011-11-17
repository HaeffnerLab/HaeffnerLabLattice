import time
import numpy
import labrad
import numpy

cxn = labrad.connect()
fc = cxn.freqcounter
dv = cxn.data_vault

#measuring channels 1 and 2, both with time period of 1 second
for channel in [0]:
    fc.set_collection_time(channel, 1.0)
for channel in [1]:
    fc.set_collection_time(channel, 1.0)
#set up data vault structure
dv.cd(['','QuickMeasurements'],True)
dv.new('Magnetic Field Flux Gate',[('Time', 'sec')], [('B field','Gauss','Axis 1'), ('B field','Gauss','Axis 2')] )
#record
def FreqToBField(freq):
    """Takes period of oscillation in Hz and Converts to Gauss using a linear relationship"""
    period = 1. / freq
    m = 1.2 / 8 #slope in gauss / microseconds
    bfield = -0.6 +  m * (period  * 10.0**6 - 10)
    return bfield

for i in range(3600 * 24):
    raw0 = numpy.array(fc.get_all_counts(0).asarray)
    raw1 = numpy.array(fc.get_all_counts(1).asarray)
    print 'count ', i
    if len(raw0) and len(raw1):
        #selecting first data point
        t =  numpy.transpose(raw0)[1][0]
        freq0 =  numpy.transpose(raw0)[0][0]
        freq1 = numpy.transpose(raw1)[0][0]
        bfield0 = FreqToBField(freq0)
        bfield1 = FreqToBField(freq1)
        dv.add([t, bfield0, bfield1 ])
        print 'measure magnetic field ', bfield0,  bfield1
    time.sleep(1)

