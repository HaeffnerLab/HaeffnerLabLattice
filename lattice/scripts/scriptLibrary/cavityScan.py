import numpy
import time

def scanCavity(cxn, cxnlab, ch, resolution, min, max, average, delay = .1):
    ld = cxnlab.laserdac
    pmt = cxn.normalpmtflow
    dv = cxn.data_vault
    dv.cd(['','CavityScans'],True)
    dv.new('Cavity Scan {}'.format(ch),[('Cavity Voltage', 'mV')], [('PMT Counts','Counts','Counts')] )
    dv.add_parameter('cavity channel', ch)
    dv.add_parameter('plotLive',True)
    if ch not in ld.getchannelnames(): raise Exception('{} channel not available'.format(ch))
    initvalue = ld.getvoltage(ch)    
    print 'moving cavity {} to minimum position'.format(ch)
    delta = resolution
    if min < initvalue: delta = -resolution
    for voltage in numpy.arange(initvalue,min, delta):
        ld.setvoltage(ch,voltage)
        print voltage
        time.sleep(.1)
    print 'performing the scan'
    for voltage in numpy.arange(min,max,resolution):
        ld.setvoltage(ch,voltage)
        counts =  pmt.get_next_counts('ON',average,True)
        dv.add([voltage,counts])
        print voltage
    print 'moving cavity to initial position'
    delta = resolution
    if min < initvalue: delta = -resolution
    for voltage in numpy.arange(max,initvalue,delta):
        ld.setvoltage(ch,voltage)
        print voltage
        time.sleep(.1)