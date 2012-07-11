import labrad
import time

#global variables
CHANNELS = ['397Table','866Table','422Table', '397Intensity']
RESOLUTION = .01 # seconds

#servers
cxn = labrad.connect()
dv = cxn.data_vault
adc = cxn.adcserver

#set up data vault
dv.cd(['','QuickMeasurements','Power Monitoring'],True)
dependVariables = [('Power',channelName,'mV') for channelName in CHANNELS]
dv.new('Power Measurement',[('Time', 'sec')], dependVariables )
tinit = time.time()
dv.add_parameter('Window',['Power Measurement'])
dv.add_parameter('plotLive','True')
dv.add_parameter('startTime',tinit)

measure = True
while True:
    try:
        if not measure: break
        reading = []
        t = time.time() - tinit
        reading.append(t)
        for channel in CHANNELS:
            channel = str(channel)
            voltage = int(adc.measurechannel(channel))
            reading.append(voltage)
        dv.add(reading)
        print 'measured time {}'.format(float(reading[0])), zip(CHANNELS, reading[1:])
        time.sleep(RESOLUTION)
    except Exception ,e:
        print e
        measure = False
        print 'stopping gracefully'
        cxn.disconnect()
        time.sleep(1)