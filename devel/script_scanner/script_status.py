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
        print self.status
    
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
            print self.status
    
    def stop(self):
        self.should_stop = True
        self.status = 'Stopping'
        #if was paused, unpause:
        if self.pause_lock.locked:
            self.pause_lock.release()
        print self.status
    
    def stop_confirmed(self):
        self.should_stop = False
        self.status = 'Stopped'
        print self.status
    
    def checking_for_pause(self):
        if self.pause_lock.locked:
            self.status = 'Paused'
            print self.status
    
    def finish_confirmed(self):
        self.percentage_complete = 100.0
        self.status = 'Finished'
        print self.status