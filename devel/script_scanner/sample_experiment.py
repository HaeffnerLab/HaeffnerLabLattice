import time
import labrad

class sample_experiment(object):
    
    def __init__(self):
        self.param = 3.0
    
    @classmethod
    def name(cls):
        return 'sample_experiment'
    
    @classmethod
    def required_parameters(cls):
        return ['parameter']
   
    def initialize(self, connection, launch_id):
        print 'in initialize', self.name(), launch_id
        
    def set_parameter(self, param_name, param):
        self.param = param
        
    def run(self):
        print 'in running', self.name()
        for i in range(1):
            print i
            time.sleep(1)
            
    def finalize(self):
        print 'exiting', self.name()

if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    from scan_methods import single_run, repeat_measurement
    ident = scanner.register_external_launch(sample_experiment.name())
    print ident
#    exprt = single_run(test1)
    exprt = repeat_measurement(sample_experiment, 1000)
    exprt.execute(ident)