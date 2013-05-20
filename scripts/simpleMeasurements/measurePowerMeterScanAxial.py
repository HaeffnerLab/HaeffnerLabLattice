import labrad
import numpy as np
import time
from matplotlib import pyplot

'''Calibrates double passes using the power meter server'''
#servers
cxn = labrad.connect()
cxnlab = labrad.connect('192.168.169.49')
dv = cxn.data_vault

def record():
    rs = cxnlab.rohdeschwarz_server
    rs.select_device(0)
    pm = cxn.power_meter_server
    pm.select_device(0)
    pm.auto_range()
    #global variables
    minpower = -60.0
    maxpower = -0.1#-0.1max #5.0 for axial
    steps = 2
    AOpowers = np.linspace(minpower, maxpower, steps)
    #measurement part
    dv.cd(['','QuickMeasurements'],True)
    name = dv.new('Single Pass LR calibration',[('Power', 'dBm')], [('Power', 'Power','mW')] )
    dv.add_parameter('plotLive',True)
    lightarr = []
    rs.amplitude(minpower)
    time.sleep(1.0)
    for power in AOpowers:
        print 'setting power to {}'.format(power)
        rs.amplitude(power)
        time.sleep(.05)
        lightmw = pm.measure().inUnitsOf('mW')
        time.sleep(.05)
        dv.add(power, lightmw)
        lightarr.append(lightmw)
    print name
    
def analyze(number):
    dv.cd(['','QuickMeasurements'],True)
    name = 'Single Pass Calibration. Quick Measurements: {}'.format(number)
    dv.open(number)
    AOpowers,lightarr = np.transpose(dv.get().asarray)
    pyplot.figure()
    ax = pyplot.subplot(211)
    pyplot.plot(AOpowers,lightarr)
    pyplot.title(name)
    pyplot.xlabel('dBm')
    pyplot.ylabel('mW')
    pyplot.grid(True,'both')
    #fit = np.polyfit(AOpowers, lightarr, deg = 10)
    #powers = np.linspace(minpower, maxpower, steps*100)
    #pyplot.plot(powers,np.polyval(fit, powers))
    ax.set_yscale('log')
    pyplot.subplot(212,  sharex = ax)
    pyplot.plot(AOpowers,lightarr)
    pyplot.show()

#record()
analyze(147)