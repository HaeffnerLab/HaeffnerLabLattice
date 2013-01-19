from script_status import script_semaphore
from twisted.internet.defer import inlineCallbacks
from twisted.internet.threads import blockingCallFromThread
from twisted.internet import reactor
from numpy import linspace
from labrad.units import WithUnit

class scan_method(object):
    
    def __init__(self, script):
        self.status = script_semaphore()
        self.script = script()
    
    def execute(self):
        '''
        implemented by the subclass
        '''

class repeat_script(scan_method):
    
    def __init__(self, script, repeatitions):
        super(repeat_script,self).__init__(script)
        self.repeatitions = repeatitions
    
    def execute(self):
        self.status.launch_confirmed()
        for i in range(self.repeatitions):
            blockingCallFromThread(reactor, self.status.pause_lock.acquire)
            self.status.pause_lock.release()
            if self.status.should_stop:
                self.script.exit()
                self.status.stop_confirmed()
                return False
            else:
                self.script.run()
                self.status.set_percentage( (i + 1.0) / self.repeatitions)
        self.script.exit()
        self.status.finish_confirmed()
        return True

class scan_script_1D(scan_method):
    def __init__(self, script, parameter, minim, maxim, steps, units):
        super(scan_script_1D,self).__init__(script)
        self.parameter = parameter
        self.scan_points = linspace(minim, maxim, steps)
        self.scan_points = [WithUnit(pt, units) for pt in self.scan_points ]
    
    def execute(self):
        self.status.launch_confirmed()
        for i in range(len(self.scan_points)):
            blockingCallFromThread(reactor, self.status.pause_lock.acquire)
            self.status.pause_lock.release()
            if self.status.should_stop:
                self.script.exit()
                self.status.stop_confirmed()
                return False
            else:
                self.script.set_parameter(self.parameter, self.scan_points[i])
                self.script.run()
                self.status.set_percentage( (i + 1.0) / len(self.scan_points))
        self.script.exit()
        self.status.finish_confirmed()
        return True