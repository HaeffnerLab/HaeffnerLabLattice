import labrad
import numpy as np
import time
from matplotlib import pyplot
from labrad.units import WithUnit

'''Calibrates double passes using the power meter server'''
#servers
cxn = labrad.connect()
cxnlab = labrad.connect('192.168.169.49')
dv = cxn.data_vault
frequency_scan_no_unit=np.linspace(70.0,100.0,10)
frequency_scan=[WithUnit(pt, 'MHz') for pt in frequency_scan_no_unit]

frequency_default = WithUnit(90.0,'MHz')

amplitude_default = WithUnit(-12.0,'dBm')

amplitude_scan_no_unit=np.linspace(-33.0,-12.0,50)
amplitude_scan=[WithUnit(pt, 'dBm') for pt in amplitude_scan_no_unit]

points_per_frequency = 2

#print frequency_scan
#print amplitude_scan

def take_freq_response():
    #cxn.pulser.frequency('global397')
    cxn.pulser.frequency('global397', WithUnit(90.0, 'MHz'))
    cxn.pulser.amplitude('global397', WithUnit(-16.0, 'dBm'))
    cxn.power_meter_server.select_device(0)
    cxn.power_meter_server.set_wavelength(397)
    dv.cd(['','QuickMeasurements'],True)
    name = dv.new('AO freq response',[('Frequency', 'MHz')], [('Power', 'Power','mW')] )
    dv.add_parameter('plotLive',True)

    
    power_array = []
    
    for i,frequency_397 in enumerate(frequency_scan):
        cxn.pulser.frequency('global397', frequency_397)
        measured_power = []
        for j in range(points_per_frequency):
            power = cxn.power_meter_server.measure()
            time.sleep(0.3)
            measured_power.extend(np.array([power['W']]))
            print j
        averaged_power = np.average(measured_power)
        power_array.extend(np.array([averaged_power]))
        frequency_397_no_unit = frequency_397['MHz']
        print frequency_397
        dv.add([frequency_397_no_unit,averaged_power]) 

       
    
    return power_array

def take_ao_power_response():
    #cxn.pulser.frequency('global397')
    cxn.pulser.frequency('global397', WithUnit(100.0, 'MHz'))
    cxn.pulser.amplitude('global397', WithUnit(-12.0, 'dBm'))
    cxn.power_meter_server
    cxn.power_meter_server.select_device(0)
    cxn.power_meter_server.set_wavelength(397)
    
    dv.cd(['','QuickMeasurements'],True)
    name = dv.new('AO power response',[('Power', 'dBm')], [('Power', 'Power','mW')] )
    dv.add_parameter('plotLive',True)
    
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
        power_397_no_unit = power_397['dBm']
        dv.add([power_397_no_unit,averaged_power])
        
    return power_array

#measured_power_array = take_ao_power_response()

def get_calibrated_frequency_scan():
    cxn.power_meter_server
    cxn.power_meter_server.select_device(0)
    cxn.power_meter_server.set_wavelength(397)
    target_power = 55.0e-6
    tolerance = 1.0e-6
    calibrated_power = []
    cxn.pulser.amplitude('global397', WithUnit(-12.0, 'dBm'))
    
    for i,frequency_397 in enumerate(frequency_scan):
        amplitude = -12.0
        cxn.pulser.amplitude('global397', WithUnit(amplitude, 'dBm'))
        cxn.pulser.frequency('global397', frequency_397)
        measured_power = []
        for j in range(points_per_frequency):
            power = cxn.power_meter_server.measure()
            time.sleep(0.1)
            measured_power.extend(np.array([power['W']]))
        averaged_power = np.average(measured_power)
        step = 1.0

        for i in range(10):
            step = step/(2.0**i)    
            difference_1 = averaged_power-target_power
            if difference_1>0.0:
                amplitude = amplitude-step
                amplitude_decreased = True
            else:
                amplitude = amplitude+step
                amplitude_decreased = False
                    
            measured_power = []
            
            for j in range(points_per_frequency):
                power = cxn.power_meter_server.measure()
                time.sleep(0.1)
                measured_power.extend(np.array([power['W']]))
                averaged_power = np.average(measured_power)  
                 
            difference_2 = averaged_power-target_power
            if (np.absolute(difference_2)>np.absolute(difference_1)):
                
                continue
            
                     
            
            
            
            
            
            while (np.absolute(averaged_power-target_power)>0.0):
                amplitude=amplitude-step
                cxn.pulser.amplitude('global397', WithUnit(amplitude, 'dBm'))
                measured_power = []
                for j in range(points_per_frequency):
                    power = cxn.power_meter_server.measure()
                    time.sleep(0.1)
                    measured_power.extend(np.array([power['W']]))
                    averaged_power = np.average(measured_power)
                print amplitude
            calibrated_power.extend(np.array([amplitude]))
    return calibrated_power

def calibrated_scan(calibrated_power):
    #cxn.pulser.frequency('global397')
    cxn.pulser.frequency('global397', WithUnit(90.0, 'MHz'))
    cxn.pulser.amplitude('global397', WithUnit(-16.0, 'dBm'))
    cxn.power_meter_server.select_device(0)
    cxn.power_meter_server.set_wavelength(397)
    dv.cd(['','QuickMeasurements'],True)
    name = dv.new('AO freq response',[('Frequency', 'MHz')], [('Power', 'Power','mW')] )
    dv.add_parameter('plotLive',True)

    
    power_array = []
    
    for i,frequency_397 in enumerate(frequency_scan):
        cxn.pulser.frequency('global397', frequency_397)
        print i,frequency_397
        cxn.pulser.amplitude('global397',WithUnit(calibrated_power[i],'dBm'))
        print calibrated_power[i]
        measured_power = []
        for j in range(points_per_frequency):
            time.sleep(0.3)
            power = cxn.power_meter_server.measure()
            measured_power.extend(np.array([power['W']]))
            #print j
        averaged_power = np.average(measured_power)
        power_array.extend(np.array([averaged_power]))
        frequency_397_no_unit = frequency_397['MHz']
        #print frequency_397
        dv.add([frequency_397_no_unit,averaged_power]) 
    
    
        

calibrated_power = get_calibrated_frequency_scan()
print calibrated_power
calibrated_scan(calibrated_power)