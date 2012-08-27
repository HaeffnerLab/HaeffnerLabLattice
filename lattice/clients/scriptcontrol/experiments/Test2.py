#import threading
import time
import sys


#class Script(threading.Thread):
class Test2():
    def __init__(self):
        self.experimentPath = ['Test', 'Exp2']
        print 'Initializing Test2'
        self.iterations = 5
        self.progress = 0.0
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
            self.progress = ((i)/float(self.iterations))*100
            Continue = self.pause(self.progress)
            if (Continue == False):
                self.cxn.semaphore.finish_experiment(self.experimentPath, self.progress)
                return
            
            time.sleep(1)
            #print 'Test parameters: ', self.parameters
            print 'goodbye'

        self.progress = 100.0   
        self.cleanUp()
        
    def cleanUp(self):
        self.cxn.semaphore.finish_experiment(self.experimentPath, self.progress)
        print 'all cleaned up boss'

if __name__ == '__main__':
    test2 = Test2()
    test2.run()