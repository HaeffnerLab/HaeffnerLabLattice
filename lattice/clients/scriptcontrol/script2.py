import threading
import time


class Script2(threading.Thread):
    def __init__(self):
        print 'not gonna do anything!'
        threading.Thread.__init__(self)
        
    def run(self):
        import labrad
        cxn = labrad.connect()
        print 'doing laborious calculation!'
        time.sleep(5)
        cxn.semaphore.set_value()
        cxn.semaphore.set_flag(False)

        
        
if __name__ == '__main__':
    script2 = Script2()
