#import threading
import time


#class Script4(threading.Thread):
class Script4():
    def __init__(self):
        print 'Initializing Script 4'
#        threading.Thread.__init__(self)
        
    def run(self):
        import labrad
        cxn = labrad.connect()
        print 'Script 4: doing laborious calculation!'
        time.sleep(3)
        cxn.semaphore.set_value2()
        cxn.semaphore.set_flag2(False)
        value = cxn.semaphore.get_value2()
        if (value == 10):
            print 'we drifted way too much, killing main script!'
            cxn.semaphore.set_kill_switch2(True)

        
        
if __name__ == '__main__':
    script2 = Script2()
    script2.start()
