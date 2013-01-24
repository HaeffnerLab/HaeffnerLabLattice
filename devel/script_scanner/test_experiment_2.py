import time
import labrad

def ScriptScanner_Experiment(object):
    '''
    Base class for all experiments controlled by the Script Scanner Server
    '''
    
    def __init__(self, scipt_id = None):
        '''
        Establish 
        '''
        self.cxn = labrad.connect()
        self.script_id = script_id
        if self.script_id is None:
            self.script_id = self.cxn.scriptscanner.register_external_run()
    
    def external_run():
        self.
        
    

class test2(object):
    
    def __init__(self, script_id):
        self.ident = script_id
        self.param = 3.0
    
    @classmethod
    def required_parameters(cls):
        return ['parameter']
    
    def initialize(self, launch_id):
        print 'starting {}'.format(self.__class__)
        print 'launch_id {}'.format(launch_id)
        cxn = labrad.connect()
        scanner = cxn.scriptscanner
        self.param = 'blank'
#        raise Exception("bah")
        
    def set_parameter(self, param_name, param):
        self.param = param
        
    def run(self):
        print self.param
        for i in range(1):
            print i
            time.sleep(1)
            
    def exit(self):
        print 'exiting'

if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    script_id = scanner.register_external_launch()
    experiment = test2(script_id)