import labrad
import numpy
import time

#calibrates the doulbe pass using ADC

#servers
cxn = labrad.connect()
dv = cxn.data_vault
dp = cxn.double_pass
pmt = cxn.normalpmtflow

#global variables
DOUBLE_PASS = 'radial'; dp.select(DOUBLE_PASS)
NUM_STEP_FREQ = 20
AVERAGE_POINTS = 5#how many output points to average
MIN_FREQ = 220.0 #MHZ
MAX_FREQ = 250.0 #MHZ
scanList = numpy.r_[MIN_FREQ:MAX_FREQ:complex(0,NUM_STEP_FREQ)]
POWER = 1.0
#set power and turn on
dp.amplitude(POWER)
dp.output(True)

dv.cd(['','CavityScans'],True)
dv.new('DoublePass Scan {}'.format(DOUBLE_PASS),[('Frequency', 'MHz')], [('PMT Counts','Counts','Counts')] )

initFreq = dp.frequency()

for freq in scanList:
    dp.frequency(freq)
    print freq
    time.sleep(0.1)
    counts =  pmt.get_next_counts('ON',AVERAGE_POINTS,True)
    dv.add([freq,counts])

dp.frequency(initFreq) 