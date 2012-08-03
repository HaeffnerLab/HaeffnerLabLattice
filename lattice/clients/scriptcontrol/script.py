import threading
import time


class Script(threading.Thread):
    def __init__(self):
        print 'not gonna do anything!'
        threading.Thread.__init__(self)
        
    def run(self):
        import labrad
        cxn = labrad.connect()
        for i in range(1000):
           # blocking function goes here
           result = cxn.semaphore.block()
           value = cxn.semaphore.get_value()
           print result
           print i
           print value

if __name__ == '__main__':
    script = Script()
