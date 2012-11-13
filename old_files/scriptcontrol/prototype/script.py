#import threading
import time
import sys


#class Script(threading.Thread):
class Script():
    def __init__(self):
        print 'Initializing Script 1'
        #threading.Thread.__init__(self)
    
    def pause(self):
        result = self.cxn.semaphore.block()
        print result
        if (result == True):
            return True
        else:
            return False

        
    def run(self):
        import labrad
        self.cxn = labrad.connect()
        for i in range(1000):
           # blocking function goes here
           result = self.pause()
           if (result == True):
               self.cleanUp()
               break

           value = self.cxn.semaphore.get_value()
           print 'Script 1: Drift Value: ', value

    def cleanUp(self):
        print 'all cleaned up boss'

if __name__ == '__main__':
    script = Script()
