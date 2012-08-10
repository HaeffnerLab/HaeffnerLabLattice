#import threading
import time


#class Script2(threading.Thread):
class Script2():
    def __init__(self):
        print 'Initializing Script 2'
        #threading.Thread.__init__(self)
        
    def run(self):
        import labrad
        cxn = labrad.connect()
        print 'Script 2: doing laborious calculation!'
        time.sleep(3)
        cxn.semaphore.set_value()
        cxn.semaphore.set_flag(False)
        value = cxn.semaphore.get_value()
        if (value == 10):
            print 'we drifted way too much, killing main script!'
            cxn.semaphore.set_kill_switch(True)

        
        
if __name__ == '__main__':
    script2 = Script2()
    script2.start()
