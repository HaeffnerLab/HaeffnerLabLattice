import time

class test1(object):
    
    def __init__(self):
        self.param = 3.0
    
    @classmethod
    def required_parameters(cls):
        return ['parameter']
    
    def initialize(self):
        print 'initializing', time.time()
        self.param = None
        
    def set_parameter(self, param_name, param):
        self.param = param
        
    def run(self):
        print 'running', time.time()
        print self.param
        time.sleep(1)
    
    def exit(self):
        print 'exiting'

if __name__ == '__main__':
    required = test1.required_parameters()
    print required
    inst = test1()
    for i in range(10):
        inst.set_parameter(i)
        inst.run()
    inst.stop()
    del inst