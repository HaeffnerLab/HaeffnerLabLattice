import time
        
class TDSMeasure():
    
    def __init__(self):
        self.experimentPath = ['SimpleMeasurements', 'TDSMeasure']
        self.d = {
                  'measure_channels':['SimpleMeasurements', 'TDSMeasure', 'measure_channels' ],
                  'resolution_path' : ['SimpleMeasurements', 'TDSMeasure', 'resolution'],
                  'iteration_path' : ['SimpleMeasurements', 'TDSMeasure', 'iterations'],
                  'saving_directory' : ['SimpleMeasurements', 'TDSMeasure', 'saving_directory'],
                  'window_name' : ['SimpleMeasurements', 'TDSMeasure', 'window_name'],
                  'plotLive' : ['SimpleMeasurements', 'TDSMeasure', 'plotLive']
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
        self.tek = cxn.tektronix_server
        print self.tek.list_devices()
        while True:
            try:
                dev = int(raw_input("Please select a device: "))
                self.tek.select_device(dev)
                break
            except:
                print "No such device."
        """
        self.channels = self.sem.get_parameter(self.d['measure_channels'])
        self.resolution = self.sem.get_parameter(self.d['resolution_path'])[2].inUnitsOf('s')
        self.iterations = int(self.sem.get_parameter(self.d['iteration_path'])[2].value)
        self.saving_directory = self.sem.get_parameter(self.d['saving_directory'])
        self.window_name = self.sem.get_parameter(self.d['window_name'])
        self.plotLive = self.sem.get_parameter(self.d['plotLive'])
        print 'Measuring Channels {}'.format(self.channels)
        """
        self.setup_data_vault()
        
    def setup_data_vault(self):
        self.dv.cd(['','QuickMeasurements','Scope Measurements', str(time.strftime("%Y%b%d",time.localtime()))], True)
        dependVariables = [('Volts', '1', 'V')] #[('Volts',channelName,'V') for channelName in self.channels]
        self.dv.new('Voltage Measurement',[('Time', 'sec')], dependVariables )
        self.dv.add_parameter('Window',['Voltage Measurement'])
        self.dv.add_parameter('plotLive','True')
        self.tinit = time.time()
        self.dv.add_parameter('startTime', self.tinit)
    
    def sequence(self):
        for i in range(10000): #(self.iterations):
            # blocking function goes here
            percentDone = 100.0 * i / 10 #self.iterations
            #cont = self.sem.block_experiment(self.experimentPath, percentDone)
            #if not cont:
            if percentDone == 100.0:
                break
            else:
                reading = []
                t = time.time() - self.tinit
                reading.append(t)
                """
                for channel in self.channels:
                    channel = str(channel)
                    voltage = int(self.tds.measure(channel))
                    reading.append(voltage)
                """
                voltage = int(self.tek.measure(1))
                reading.append(voltage)
                self.dv.add(reading)
                # print 'measured time {}'.format(float(reading[0])), zip(self.channels, reading[1:])
                time.sleep(0.5) #self.resolution)

    def finalize(self):
        #self.sem.finish_experiment(self.experimentPath)
        #self.cxn.disconnect()
        print 'Finished: {}'.format(self.experimentPath)

if __name__ == '__main__':
    exprt = TDSMeasure()
    exprt.run()
