import time
import labrad

class test1(object):
    
    def __init__(self):
        self.param = 3.0
    
    @classmethod
    def required_parameters(cls):
        return ['parameter']
   
    def initialize(self, connection, launch_id):
#        import labrad
        print launch_id, connection._ctx
#        print 's    import labradtarting {}'.format(self.__class__)
#        print 'launch_id {}'.format(launch_id)
#        cxn = labrad.connect()
#        scanner = cxn.scriptscanner
#        self.param = 'blank'
#        raise Exception("bah")
        
    def set_parameter(self, param_name, param):
        self.param = param
        
    def run(self):
        print self.param
        for i in range(1):
            print i
            time.sleep(1)
            
    def finalize(self):
        print 'exiting'

if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    script_id = scanner.register_external_launch()
    exprt = test1()
    exprt.initialize(script_id)
    exprt.run()
    exprt.finalize() 