import time
import numpy
import labrad
import numpy

cxn = labrad.connect()
fc = cxn.freqcounter
dv = cxn.data_vault

RESOLUTION = 1 #seconds, how often points are taken
CHANNELS = [0,1]

for channel in CHANNELS:
    fc.set_collection_time(channel, RESOLUTION)
#set up data vault structure
tinit = time.time()
dv.cd(['','QuickMeasurements'],True)
dependentVars = [('B field','Axis {}'.format(ch),'Gauss') for ch in CHANNELS]
dv.new('Magnetic Field Flux Gate',[('Time', 'sec')], dependentVars )
dv.add_parameter('plotLive',True)
dv.add_parameter('startTime',tinit)

def FreqToBField(freq):
    """Takes period of oscillation in Hz and Converts to Gauss using a linear relationship"""
    period = 1.0 / freq
    m = 1.2 / (8.0e-6) #slope in gauss / seconds
    bfield = -0.6 +  m * (period  - 10e-6) # 100 Khz which is 10 microsecond period corresponds to -0.6 Gauss
    return bfield

measure = True

while True:
    try:
        if not measure: break
        reading = []
        t = time.time() - tinit
        reading.append(t)
        for channel in CHANNELS:
            raw = fc.get_all_counts(channel).asarray
            while not len(raw): #make sure we wait for a reading
                raw = fc.get_all_counts(channel).asarray
                time.sleep(RESOLUTION)
            lastFreq = numpy.transpose(raw)[0][0]
            bfield = FreqToBField(lastFreq)
            reading.append(bfield)
        dv.add(reading)
        print 'measured time {}'.format(float(reading[0])), zip(CHANNELS, reading[1:])
        time.sleep(RESOLUTION)
    except:
        measure = False
        print 'stopping gracefully'
        cxn.disconnect()
        time.sleep(1)

