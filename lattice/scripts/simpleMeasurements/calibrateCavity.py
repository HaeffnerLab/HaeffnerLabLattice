import time
import numpy

def calibrateCavity(ch , min, max):
    RESOLUTION = 1 #resolution in mV
    SLEEP = .1 #seconds
    
    from lrexp.lr import Client
    ld = Client.connection.laserdac
    m = Client.connection.multiplexer_server
    dv = Client.connection.data_vault
    dv.cd(['','Caliibrations'],True)
    dv.new('Laser Cavity Calibration',[('Cavity Voltage', 'mV')], [('Frequency','THz','THz')] )
    dv.add_parameter('cavity channel', ch)
    
    if ch not in ld.getchannelnames(): raise
    initvalue = ld.getvoltage(ch)
    print 'initial value of channel {0} is {1}'.format(ch, initvalue)
    
    print 'moving cavity to minimum position'
    delta = RESOLUTION
    if min < initvalue: delta = -RESOLUTION
    for voltage in numpy.arange(initvalue,min, delta):
        ld.setvoltage(ch,voltage)
        print voltage
        time.sleep(SLEEP)
        
    print 'performing the calibration'
    m.select_one_channel(ch.lower())
    m.start_cycling()
    for voltage in numpy.arange(min,max,RESOLUTION):
        ld.setvoltage(ch,voltage)
        time.sleep(SLEEP)
        freq = m.get_frequency(ch.lower())
        dv.add([voltage,freq])
        print 'measured {0}mV, {1}THz'.format(voltage, freq)
    
    print 'moving cavity to initial position'
    delta = RESOLUTION
    if min < initvalue: delta = -RESOLUTION
    for voltage in numpy.arange(max,initvalue,delta):
        ld.setvoltage(ch,voltage)
        print voltage
        time.sleep(SLEEP)
        