import labrad
import numpy as np
import time
from matplotlib import pyplot
from labrad.units import WithUnit

'''Calibrates double passes using the power meter server'''
#servers
cxn = labrad.connect()
#cxnlab = labrad.connect('192.168.169.49')
dv = cxn.data_vault
frequency_scan_no_unit=np.linspace(70.0,100.0,10)
frequency_scan=[WithUnit(pt, 'MHz') for pt in frequency_scan_no_unit]

frequency_default = WithUnit(90.0,'MHz')

amplitude_default = WithUnit(-12.0,'dBm')

amplitude_scan_no_unit=np.linspace(-63.0,-12.0,10)
amplitude_scan=[WithUnit(pt, 'dBm') for pt in amplitude_scan_no_unit]

points_per_frequency = 5

#print frequency_scan
#print amplitude_scan

def take_freq_response():
    #cxn.pulser.frequency('global397')
    cxn.pulser.frequency('global397', WithUnit(90.0, 'MHz'))
    cxn.pulser.amplitude('global397', WithUnit(-12.0, 'dBm'))
    cxn.power_meter_server
    cxn.power_meter_server.select_device(0)
    cxn.power_meter_server.set_wavelength(397)
    
    power_array = []
    
    for i,frequency_397 in enumerate(frequency_scan):
        cxn.pulser.frequency('global397', frequency_397)
        measured_power = []
        for j in range(points_per_frequency):
            power = cxn.power_meter_server.measure()
            time.sleep(0.2)
            measured_power.extend(np.array([power['W']]))
            print j
        averaged_power = np.average(measured_power)
        power_array.extend(np.array([averaged_power]))
        print frequency_397
        
    return power_array

def take_ao_power_response():
    #cxn.pulser.frequency('global397')
    cxn.pulser.frequency('global397', WithUnit(90.0, 'MHz'))
    cxn.pulser.amplitude('global397', WithUnit(-12.0, 'dBm'))
    cxn.power_meter_server
    cxn.power_meter_server.select_device(0)
    cxn.power_meter_server.set_wavelength(397)
    
    power_array = []
    
    for i,power_397 in enumerate(amplitude_scan):
        cxn.pulser.amplitude('global397', power_397)
        measured_power = []
        for j in range(points_per_frequency):
            power = cxn.power_meter_server.measure()
            time.sleep(0.2)
            measured_power.extend(np.array([power['W']]))
            print j
        averaged_power = np.average(measured_power)
        power_array.extend(np.array([averaged_power]))
        print power_397
        
    return power_array

#measured_power_array = take_freq_response()

pyplot.figure()
pyplot.plot(amplitude_scan_no_unit,take_ao_power_response())
pyplot.show()