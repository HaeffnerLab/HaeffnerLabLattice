from script_status import script_semaphore
#from twisted.internet.defer import inlineCallbacks
from twisted.internet.threads import blockingCallFromThread
from twisted.internet import reactor
from numpy import linspace
from labrad.units import WithUnit

class scan_method(object):
    
    def __init__(self, scan_name, script):
        self.status = script_semaphore()
        self.script = script()
        self.scan_name = scan_name
    
    def execute(self, ident):
        '''
        implemented by the subclass
        '''
        try:
            self.script.initialize(ident)
            self.status.launch_confirmed()
            self.execute_scan()
            self.script.exit()
        except Exception as e:
            print e
            self.status.error_finish_confirmed(e)
        else:
            self.status.finish_confirmed()
            return True
    
    def pause_or_stop(self):
        self.status.checking_for_pause()
        blockingCallFromThread(reactor, self.status.pause_lock.acquire)
        self.status.pause_lock.release()
        if self.status.should_stop:
            self.status.stop_confirmed()
            return True
    
    def execute_scan(self):
        '''
        implemented by the subclass
        '''    

class repeat_script(scan_method):
    
    def __init__(self, scan_name, script, repeatitions):
        self.repeatitions = repeatitions
        scan_name = self.name_format(scan_name)
        super(repeat_script,self).__init__(scan_name, script)

    def name_format(self, name):
        if self.repeatitions == 1:
            return name
        else:
            return 'Repeat {0} {1} times'.format(name, self.repeatitions)
    
    def execute_scan(self):
        for i in range(self.repeatitions):
            if self.pause_or_stop(): return
            self.script.run()
            self.status.set_percentage( (i + 1.0) / self.repeatitions)

class scan_script_1D(scan_method):
    def __init__(self, scan_name, script, parameter, minim, maxim, steps, units):
        scan_name = self.name_format(scan_name)
        super(scan_script_1D,self).__init__(scan_name, script)
        self.parameter = parameter
        self.scan_points = linspace(minim, maxim, steps)
        self.scan_points = [WithUnit(pt, units) for pt in self.scan_points ]
        
    def name_format(self, name):
        return 'Scanning {0} in {1}'.format(self.parameter, name)
    
    def execute_scan(self):
        for i in range(len(self.scan_points)):
            if self.pause_or_stop(): return
            self.script.set_parameter(self.parameter, self.scan_points[i])
            self.script.run()
            self.status.set_percentage( (i + 1.0) / len(self.scan_points))