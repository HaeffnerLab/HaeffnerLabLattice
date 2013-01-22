import time
import labrad

class test1(object):
    
    def __init__(self):
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
    required = test1.required_parameters()
    print required
    #external registration