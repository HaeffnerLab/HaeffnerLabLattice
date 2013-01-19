from script_status import script_semaphore
from twisted.internet.defer import inlineCallbacks

class scan_method(object):
    
    def __init__(self, script):
        self.status = script_semaphore()
        self.script = script
    
    def execute(self):
        '''
        implemented by the subclass
        '''

class repeat_script(scan_method):
    
    def __init__(self, script, repeatitions):
        super(repeat_script,self).__init__(script)
        self.repeatitions = repeatitions
    
    @inlineCallbacks
    def execute(self):
        self.status.launch_confirmed()
        for i in range(self.repeatitions):
            yield self.status.pause_lock()
            self.status.pause_lock.release()
            if self.status.should_stop:
                self.script.exit()
                self.status.stop_confirmed()
                break
            else:
                self.script.run()
                self.status.set_percentage( (i + 1.0) / self.repeatitions)
                self.script.exit()
                self.script.finish_confirmed()