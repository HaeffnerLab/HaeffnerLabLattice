from twisted.internet.defer import inlineCallbacks, DeferredLock

class script_semaphore(object):
    '''class for storing information about runtime behavior script'''
    #need signal for notifications
    def __init__(self):
        self.pause_lock = DeferredLock()
        self.status = 'Ready'
        self.percentage_complete = 0.0
        self.should_stop = False
    
    def set_percentage(self, perc):
        if not 0.0 <= perc <= 100.0: raise Exception ("Incorrect Percentage of Completion")
        self.percentage_complete = perc
    
    def launch_confirmed(self):
        self.status = 'Running'
    
    @inlineCallbacks
    def pause(self, should_pause):
        if should_pause:
            self.status = 'Pausing'
            yield self.pause_lock.acquire()
            self.status = 'Paused'
        else:
            self.pause_lock.release()
            self.status = 'Running'
    
    def stop(self):
        self.should_stop = True
        self.status = 'Stopping'
    
    def stop_confirmed(self):
        self.should_stop = False
        self.status = 'Stopped'
    
    def finish_confirmed(self):
        self.percentage_complete = 100.0
        self.status = 'Finished'