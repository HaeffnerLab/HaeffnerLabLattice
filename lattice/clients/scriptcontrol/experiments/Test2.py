#import threading
import time
import sys


#class Script(threading.Thread):
class Test2():
    def __init__(self):
        self.experimentName = 'Test2'
        print 'Initializing Test2'
        #threading.Thread.__init__(self)
    
    def pause(self):
        Continue = self.cxn.semaphore.block_experiment(self.experimentName)
        if (Continue == True):
            self.parameters = self.cxn.semaphore.script_request_experiment_parameters(self.experimentName)
            return True
        else:
            return False
         
    def run(self):
        import labrad
        self.cxn = labrad.connect()
        for i in range(1000):
            # blocking function goes here
            Continue = self.pause()
            if (Continue == False):
                self.cleanUp()
                break
            
            print 'Test2 parameters: ', self.parameters

    def cleanUp(self):
        print 'all cleaned up boss'

if __name__ == '__main__':
    test2 = Test2()
    test2.run()
