from FFT import measureFFT
import numpy as np
import labrad
import time

cxn = labrad.connect()
dv = cxn.data_vault
hv = cxn.highvolta

voltageMin = 0.0
VoltageMax = 4000.0
VoltageStep = 250.0
voltagesettime = 1.0
recordTime = 0.5 #seconds
average = 4
freqSpan = 300.0 #Hz 
freqOffset = -310.0 #Hz, the offset between the counter clock and the rf synthesizer clock
#setting up FFT
fft = measureFFT(cxn, recordTime, average, freqSpan, freqOffset, savePlot = False)
#saving
dv.cd(['','QuickMeasurements','FFT'],True)
name = dv.new('FFT',[('Voltage', 'V')], [('FFTPeak','Arb','Arb')] )
dv.add_parameter('plotLive',True)
print 'Saving {}'.format(name)

voltages = np.arange(voltageMin, VoltageMax + VoltageStep, VoltageStep)
initvoltage = hv.getvoltage()
for voltage in voltages:
    hv.setvoltage(voltage)
    time.sleep(voltagesettime)
    micromotion = fft.getPeakArea(ptsAround = 3)
    dv.add(voltage, micromotion)
hv.setvoltage(initvoltage)