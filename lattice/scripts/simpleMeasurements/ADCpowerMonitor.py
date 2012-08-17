import time
        
class ADCPowerMonitor():
    
    def __init__(self):
        self.experimentPath = ['SimpleMeasurements', 'ADCPowerMonitor']
        self.d = {
                  'measure_channels':['SimpleMeasurements', 'ADCPowerMonitor', 'measure_channels' ],
                  'resolution_path' : ['SimpleMeasurements', 'ADCPowerMonitor', 'resolution'],
                  'iteration_path' : ['SimpleMeasurements', 'ADCPowerMonitor', 'iterations'],
                  'saving_directory' : ['SimpleMeasurements', 'ADCPowerMonitor', 'saving_directory'],
                  'window_name' : ['SimpleMeasurements', 'ADCPowerMonitor', 'window_name'],
                  'plotLive' : ['SimpleMeasurements', 'ADCPowerMonitor', 'plotLive']
                  }        

    def run(self):
        self.initialize()
        self.sequence()
        self.finalize()

    def initialize(self):
        print 'Started: {}'.format(self.experimentPath)
        import labrad
        self.cxn = cxn = labrad.connect()
        self.sem = cxn.semaphore
        self.dv = cxn.data_vault
        self.adc = cxn.adcserver
        self.channels = cxn.semaphore.get_parameter(self.d['measure_channels'])
        self.resolution = cxn.semaphore.get_parameter(self.d['resolution_path'])[2].inUnitsOf('s')
        self.iterations = int(cxn.semaphore.get_parameter(self.d['iteration_path'])[2].value)
        self.saving_directory = cxn.semaphore.get_parameter(self.d['saving_directory'])
        self.window_name = cxn.semaphore.get_parameter(self.d['window_name'])
        self.plotLive = cxn.semaphore.get_parameter(self.d['plotLive'])
        print 'Measuring Channels {}'.format(self.channels)
        self.setup_data_vault()
        
    def setup_data_vault(self):
        self.dv.cd(['','QuickMeasurements','Power Monitoring'],True)
        dependVariables = [('Power',channelName,'mV') for channelName in self.channels]
        self.dv.new('Power Measurement',[('Time', 'sec')], dependVariables )
        self.dv.add_parameter('Window',['Power Measurement'])
        self.dv.add_parameter('plotLive','True')
        self.tinit = time.time()
        self.dv.add_parameter('startTime', self.tinit)
    
    def sequence(self):
        for i in range(self.iterations):
            # blocking function goes here
            percentDone = 100.0 * i / self.iterations
            cont = self.sem.block_experiment(self.experimentPath, percentDone)
            if not cont:
                break
            else:
                reading = []
                t = time.time() - self.tinit
                reading.append(t)
                for channel in self.channels:
                    channel = str(channel)
                    voltage = int(self.adc.measurechannel(channel))
                    reading.append(voltage)
                self.dv.add(reading)
                print 'measured time {}'.format(float(reading[0])), zip(self.channels, reading[1:])
                time.sleep(self.resolution)

    def finalize(self):
        self.sem.finish_experiment(self.experimentPath)
        self.cxn.disconnect()
        print 'Finished: {}'.format(self.experimentPath)

if __name__ == '__main__':
    exprt = ADCPowerMonitor()
    exprt.run()
