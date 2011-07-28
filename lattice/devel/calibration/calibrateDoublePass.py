import labrad
import numpy
import time

cxn = labrad.connect()
sigGen = cxn.lattice_pc_rs_server_blue
dv = cxn.data_vault

STEP_FREQ = .1
MIN_FREQ = 70 #MHZ
MAX_FREQ = 80 #MHZ

sigGen.setpower(17.5)

scanList = numpy.arange(MIN_FREQ,MAX_FREQ,STEP_FREQ)
for freq in scanList:
    sigGen.setfreq(freq)
    power = 23 - (freq - MIN_FREQ)*.55
    print power
    sigGen.setpower(power)
    time.sleep(.5)
    
    