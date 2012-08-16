#set up data vault
#dv.cd(['','QuickMeasurements','Power Monitoring'],True)
#dependVariables = [('Power',channelName,'mV') for channelName in CHANNELS]
#dv.new('Power Measurement',[('Time', 'sec')], dependVariables )
#tinit = time.time()
#dv.add_parameter('Window',['Power Measurement'])
#dv.add_parameter('plotLive','True')
#dv.add_parameter('startTime',tinit)
#
#measure = True
#while True:
#    try:
#        if not measure: break
#        reading = []
#        t = time.time() - tinit
#        reading.append(t)
#        for channel in CHANNELS:
#            channel = str(channel)
#            voltage = int(adc.measurechannel(channel))
#            reading.append(voltage)
#        dv.add(reading)
#        print 'measured time {}'.format(float(reading[0])), zip(CHANNELS, reading[1:])
#        time.sleep(RESOLUTION)
#    except Exception ,e:
#        print e
#        measure = False
#        print 'stopping gracefully'
#        cxn.disconnect()
#        time.sleep(1)
        
class ADCPowerMonitor():
    def __init__(self):
        self.experimentPath = ['SimpleMeasurements', 'ADCPowerMonitor']
        import labrad
        cxn = labrad.connect()
        self.sem = cxn.semaphore
        self.dv = cxn.data_vault
        self.adc = cxn.adcserver
        channel_path = ['SimpleMeasurements', 'ADCPowerMonitor', 'measure_channels' ]
        self.channels = self.sem.get_parameter_name(channel_path)
        resolution_path = ['SimpleMeasurements', 'ADCPowerMonitor', 'measure_channels']
        self.resolution =  self.sem.get_parameter_name(resolution_path)[2]
        iteration_path = ['SimpleMeasurements', 'ADCPowerMonitor', 'iterations']
        self.iterations = self.sem.get_parameter_name(iteration_path)[2]
        print 'Starting {}'.format(self.experimentPath)
    
    def pause(self, progress):
        Continue = self.cxn.semaphore.block_experiment(self.experimentPath, progress)
        if (Continue == True):
            self.parameters = self.cxn.semaphore.get_parameter_names(self.experimentPath)
            return True
        else:
            return False    
         
    def run(self):
        print 'doen'
#        
#        
#        
#        for i in range(self.iterations):
#            # blocking function goes here
#            Continue = self.pause(((i+1)/float(self.iterations))*100)
#            if (Continue == False):
#                self.cleanUp()
#                break
#            
#            print 'Test parameters: ', self.parameters

    def cleanUp(self):
        print 'all cleaned up boss'

if __name__ == '__main__':
    exprt = ADCPowerMonitor()
    exprt.run()
