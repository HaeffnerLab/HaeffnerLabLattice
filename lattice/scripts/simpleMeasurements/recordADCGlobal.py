import labrad
import time

#calibrates the doulbe pass using ADC

#servers
cxn = labrad.connect()
dv = cxn.data_vault
adc = cxn.adcserver

#global variables
CHANNEL = 'global397'
RESOLUTION = 10 # seconds
RECORDTIME = int(24*3600./RESOLUTION)  #1 hour with

#set up data vault
dv.cd(['','QuickMeasurements','Power Monitoring'],True)
dv.new('Power {}'.format(CHANNEL),[('Time', 'sec')], [('Power','Volt','Volt')] )

for i in range(RECORDTIME):
    voltage = adc.measurechannel(CHANNEL)
    t = time.time()
    dv.add([t,voltage])
    print 'measured {} {}'.format(t, voltage)
    time.sleep(RESOLUTION)