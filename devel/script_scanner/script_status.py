from twisted.internet.defer import inlineCallbacks, DeferredLock
from signals import Signals

class script_semaphore(object):
    '''class for storing information about runtime behavior script'''
###this class needs identification for signaling
    def __init__(self):
        self.pause_lock = DeferredLock()
        self.status = 'Ready'
        self.percentage_complete = 0.0
        self.should_stop = False
        self.on_new_status = Signals.on_new_status
        self.on_new_status(self.status, self.percentage_complete)
    
    def set_percentage(self, perc):
        if not 0.0 <= perc <= 100.0: raise Exception ("Incorrect Percentage of Completion")
        self.percentage_complete = perc
        #signal on new percentage
    
    def launch_confirmed(self):
        self.status = 'Running'
    
    @inlineCallbacks
    def pause(self, should_pause):
        if should_pause:
            self.status = 'Pausing'
            print self.status
            yield self.pause_lock.acquire()
        else:
            if not self.pause_lock.locked:
                raise Exception ("Trying to unpause script that was not paused")
            self.pause_lock.release()
            self.status = 'Running'
    
    def stop(self):
        self.should_stop = True
        self.status = 'Stopping'
        #if was paused, unpause:
        if self.pause_lock.locked:
            self.pause_lock.release()
    
    def stop_confirmed(self):
        self.should_stop = False
        self.status = 'Stopped'
    
    def checking_for_pause(self):
        if self.pause_lock.locked:
            self.status = 'Paused'
    
    def finish_confirmed(self):
        self.percentage_complete = 100.0
        self.status = 'Finished'
    
    def error_finish_confirmed(self, error):
        self.status = 'Error {}'.format(error)