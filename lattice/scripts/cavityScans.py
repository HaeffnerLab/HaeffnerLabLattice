import time
import numpy

def scanCavity397S(min,max):
    scanCavity('397S', 0.2, min, max)
    
def scanCavity866(min,max):
    scanCavity('866', 1, min, max)

def scanCavity(ch, resolution, min, max):
    RESOLUTION = resolution #resolution in mV
    SLEEP = .1 #seconds
    from lrexp.lr import Client
    ld = Client.connection.laserdac
    pmt = Client.connection.normalpmtflow
    dv = Client.connection.data_vault
    dv.cd(['','CavityScans'],True)
    dv.new('Cavity Scan {}'.format(ch),[('Cavity Voltage', 'mV')], [('PMT Counts','Counts','Counts')] )
    dv.add_parameter('cavity channel', ch)
    
    if ch not in ld.getchannelnames(): raise Exception('{} channel not available'.format(ch))
    initvalue = ld.getvoltage(ch)
    print 'initial value of channel {0} is {1}'.format(ch, initvalue)
    
    print 'moving cavity {} to minimum position'.format(ch)
    delta = RESOLUTION
    if min < initvalue: delta = -RESOLUTION
    for voltage in numpy.arange(initvalue,min, delta):
        ld.setvoltage(ch,voltage)
        print voltage
        time.sleep(SLEEP)
        
    print 'performing the scan'
    for voltage in numpy.arange(min,max,RESOLUTION):
        ld.setvoltage(ch,voltage)
        counts =  pmt.get_next_counts('ON',3,True)
        dv.add([voltage,counts])
        print 'measured {0}mV, {1} counts'.format(voltage, counts)
    
    print 'moving cavity to initial position'
    delta = RESOLUTION
    if min < initvalue: delta = -RESOLUTION
    for voltage in numpy.arange(max,initvalue,delta):
        ld.setvoltage(ch,voltage)
        print voltage
        time.sleep(SLEEP)

        