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
frequency_scan_no_unit=np.linspace(70.0,100.0,200)
frequency_scan=[WithUnit(pt, 'MHz') for pt in frequency_scan_no_unit]

frequency_default = WithUnit(90.0,'MHz')

amplitude_default = WithUnit(-12.0,'dBm')

amplitude_scan_no_unit=np.linspace(-33.0,-12.0,50)
amplitude_scan=[WithUnit(pt, 'dBm') for pt in amplitude_scan_no_unit]

points_per_frequency = 1

delay_time = 0.1

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
            time.sleep(delay_time)
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
            time.sleep(delay_time)
            measured_power.extend(np.array([power['W']]))
            print j
        averaged_power = np.average(measured_power)
        power_array.extend(np.array([averaged_power]))
        print power_397
        power_397_no_unit = power_397['dBm']
        dv.add([power_397_no_unit,averaged_power])
        
    return power_array


def get_calibrated_frequency_scan(calibrated_power,step):
    cxn.power_meter_server
    cxn.power_meter_server.select_device(0)
    cxn.power_meter_server.set_wavelength(397)
    target_power = 33.0e-6
    #calibrated_power = np.ones_like(frequency_scan_no_unit)*(-12.0)
    #calibrated_power=np.array([-17.078 -17.318 -17.678 -17.798 -17.788 -17.584 -16.38  -15.294 -14.738 -12.216])
    #cxn.pulser.amplitude('global397', WithUnit(-12.0, 'dBm'))
     
    for i,frequency_397 in enumerate(frequency_scan):
        amplitude = calibrated_power[i]
        cxn.pulser.amplitude('global397', WithUnit(amplitude, 'dBm'))
        print amplitude
        cxn.pulser.frequency('global397', frequency_397)
        time.sleep(delay_time)
        measured_power = []
        for j in range(points_per_frequency):
            power = cxn.power_meter_server.measure()
            time.sleep(delay_time)
            measured_power.extend(np.array([power['W']]))
        averaged_power = np.average(measured_power)
        #step = 0.002
        while (averaged_power-target_power>0.0):
            amplitude = amplitude - step
            cxn.pulser.amplitude('global397', WithUnit(amplitude, 'dBm'))        
            print amplitude               
            measured_power = []           
            for j in range(points_per_frequency):
                power = cxn.power_meter_server.measure()
                time.sleep(delay_time)
                measured_power.extend(np.array([power['W']]))
                averaged_power = np.average(measured_power)                       
        calibrated_power[i]=amplitude+step    
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
            time.sleep(delay_time)
            power = cxn.power_meter_server.measure()
            measured_power.extend(np.array([power['W']]))
            #print j
        averaged_power = np.average(measured_power)
        power_array.extend(np.array([averaged_power]))
        frequency_397_no_unit = frequency_397['MHz']
        #print frequency_397
        dv.add([frequency_397_no_unit,averaged_power]) 
    
    
        

#calibrated_power = get_calibrated_frequency_scan()
calibrated_power = np.ones_like(frequency_scan_no_unit)*(-12.0)

for i in range(7):
    calibrated_power = get_calibrated_frequency_scan(calibrated_power,2.0/(2.0**i))
    print calibrated_power
    calibrated_scan(calibrated_power)

#[-20.1875,  -20.15625, -20.125,   -20.15625 ,-20.15625, -20.1875 , -20.25, -20.34375 ,-20.375  , -20.40625 ,-20.46875 ,-20.53125, -20.5625 , -20.53125, -20.53125, -20.53125, -20.5    , -20.4375 , -20.4375 , -20.40625, -20.40625 -20.40625, -20.46875, -20.4375,  -20.4375 , -20.375 ,  -20.34375, -20.21875,-20.03125, -19.84375, -19.625 ,  -19.40625, -19.125 ,  -18.84375 ,-18.5625,-18.34375, -18.15625, -18.   ,   -17.84375, -17.78125 ,-17.6875,  -17.59375,-17.53125 ,-17.375 ,  -17.15625 ,-16.8125 , -16.40625 ,-15.90625, -15.3125,-14.75   ]
#calibrated_power=np.array([-17.078, -17.318, -17.678, -17.798, -17.788, -17.584 ,-16.38 , -15.294 ,-14.738, -12.216])
#get_calibrated_frequency_scan()

#calibrated_power=np.array([-23.8203125, -23.8203125, -24.0703125, -24.0390625, -23.8828125, -23.6640625, -22.3515625, -21.203125,  -20.7421875, -18.2265625])

#calibrated_scan(calibrated_power)