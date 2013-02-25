import labrad
from common.abstractdevices.script_scanner.scan_methods import experiment

class set_high_volt(experiment):
    
    name = 'Set High Volt'
    required_parameters = [
                           ('Misc','hv_voltage'),
                           ]
    
    def initialize(self, cxn, context, ident):
        self.hv = cxn.highvolta
        self.init_votlage = self.hv.getvoltage() 
        
    def run(self, cxn, context):
        voltage = self.parameters.Misc.hv_voltage['V']
        self.hv.setvoltage(voltage)
        
    def finalize(self, cxn, context):
        self.hv.setvoltage(self.init_votlage)

if __name__ == '__main__':
    #normal way to launch
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = set_high_volt(cxn = cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)