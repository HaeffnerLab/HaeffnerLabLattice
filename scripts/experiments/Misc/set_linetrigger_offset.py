import labrad
from common.abstractdevices.script_scanner.scan_methods import experiment

class set_linetrigger_offset(experiment):
    
    name = 'Set Linetrigger Offset'
    required_parameters = [
                           ('Misc','linetrigger_offset'),
                           ]
    
    def initialize(self, cxn, context, ident):
        self.pulser = cxn.pulser
        self.init_state = self.pulser.line_trigger_state()
        self.init_duration = self.pulser.line_trigger_duration()
        self.pulser.line_trigger_state(True)
        
    def run(self, cxn, context):
        dur = self.parameters.Misc.linetrigger_offset
        self.pulser.line_trigger_duration(dur)
        
    def finalize(self, cxn, context):
        self.pulser.line_trigger_state(self.init_state)
        self.pulser.line_trigger_duration(self.init_duration)

if __name__ == '__main__':
    #normal way to launch
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = set_linetrigger_offset(cxn = cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)