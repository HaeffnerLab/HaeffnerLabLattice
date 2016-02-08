from labrad.units import WithUnit

class agilent():
    def __init__(self, cxn, output = True, amplitude = WithUnit(23, 'dBm')):
        agi = cxn.agilent_server
        dev = agi.list_devices()[0][0]
        agi.select_device(dev)
        agi.output(output)
        agi.amplitude(amplitude)
        self.agi = agi
        
    def set_output(self, output):
        self.agi.output(output)
    
    def set_frequency(self, f):
        self.agi.frequency(f)
        
    def set_amplitude(self, a):
        self.agi.amplitude(a)