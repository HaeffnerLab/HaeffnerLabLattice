import labrad
import time

#servers
cxn = labrad.connect()
dv = cxn.data_vault
adc = cxn.adcserver

#global variables
CHANNEL = 'global397'
RESOLUTION =.1 # seconds
RECORDTIME = int(24*3600./RESOLUTION) #24 hours recording

#set up data vault
dv.cd(['','QuickMeasurements','Power Monitoring'],True)
dv.new('Power {}'.format(CHANNEL),[('Time', 'sec')], [('Power','mV','mV')] )
dv.add_parameter('plotLive','True')
tinit = time.time()
for i in range(RECORDTIME):
    voltage = adc.measurechannel(CHANNEL)
    t = time.time() - tinit
    dv.add([t,voltage])
    print 'measured {} {}'.format(t, voltage)
    time.sleep(RESOLUTION)