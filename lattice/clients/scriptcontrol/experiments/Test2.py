#import threading
import time
import sys


#class Script(threading.Thread):
class Test2():
    def __init__(self):
        self.experimentPath = ['Test', 'Exp2']
        print 'Initializing Test2'
        self.iterations = 100
        #threading.Thread.__init__(self)
    
    def pause(self, progress):
        Continue = self.cxn.semaphore.block_experiment(self.experimentPath, progress)
        if (Continue == True):
            self.parameters = self.cxn.semaphore.get_parameter_names(self.experimentPath)
            return True
        else:
            return False
         
    def run(self):
        import labrad
        self.cxn = labrad.connect()
        for i in range(self.iterations):
            # blocking function goes here
            Continue = self.pause(((i+1)/float(self.iterations))*100)
            if (Continue == False):
                self.cleanUp()
                break
            
            print 'Test2 parameters: ', self.parameters

    def cleanUp(self):
        print 'all cleaned up boss'

if __name__ == '__main__':
    test2 = Test2()
    test2.run()
