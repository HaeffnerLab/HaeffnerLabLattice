import time

class test1(object):
    
    @classmethod
    def required_parameters(cls):
        return ['parameter']
    
    def initialize(self):
        print 'initializing', time.time()
        self.param = None
        
    def set_parameter(self, param):
        self.param = param
        
    def run(self):
        print 'running'
        print self.param
    
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