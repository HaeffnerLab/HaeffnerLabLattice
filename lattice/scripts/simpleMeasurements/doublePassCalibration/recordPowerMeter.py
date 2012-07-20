import labrad
import time

#global variables
RESOLUTION = .01 # seconds

#servers
cxn = labrad.connect()
dv = cxn.data_vault
pm = cxn.power_meter_server
pm.select_device(0)
pm.auto_range()

#set up data vault
dv.cd(['','QuickMeasurements','Power Monitoring'],True)
dependVariables = [('Power',channelName,'W') for channelName in ['397']]
dv.new('Power Measurement',[('Time', 'sec')], dependVariables )
dv.add_parameter('Window',['Power Measurement'])
dv.add_parameter('plotLive','True')
tinit = time.time()
dv.add_parameter('startTime',tinit)

measure = True
while True:
    try:
        if not measure: break
        reading = pm.measure()
        reading = float(reading)
        t = time.time() - tinit
        print 'measured time {0} level {1}'.format(t, reading)
        dv.add([t, reading])
        time.sleep(RESOLUTION)
    except Exception ,e:
        print e
        measure = False
        print 'stopping gracefully'
        cxn.disconnect()