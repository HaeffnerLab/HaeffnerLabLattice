from twisted.internet.defer import inlineCallbacks, DeferredLock, Deferred
from signals import Signals

class script_semaphore(object):
    '''class for storing information about runtime behavior script'''
    def __init__(self, ident, signals):
        self.pause_lock = DeferredLock()
        self.pause_request = None
        self.continue_request = None
        self.already_called_continue = False
        self.status = 'Ready'
        self.percentage_complete = 0.0
        self.should_stop = False
        self.ident = ident
        self.signals = signals
        
    def get_progress(self):
        return (self.status, self.percentage_complete)
    
    def set_percentage(self, perc):
        if not 0.0 <= perc <= 100.0: raise Exception ("Incorrect Percentage of Completion")
        self.percentage_complete = perc
        self.signals.on_running_new_status((self.ident, self.status, self.percentage_complete))
    
    def launch_confirmed(self):
        self.status = 'Running'
        self.signals.on_running_new_status((self.ident, self.status, self.percentage_complete))
        
    @inlineCallbacks
    def pause(self):
        if self.pause_lock.locked:
            self.status = 'Paused'
            self.signals.on_running_new_status((self.ident, self.status, self.percentage_complete))
            self.signals.on_running_script_paused((self.ident, True))
            self.pause_request.callback(True)
        yield self.pause_lock.acquire()
        self.pause_lock.release()
        if self.status == 'Paused':
            self.status = 'Running'
            self.signals.on_running_new_status((self.ident, self.status, self.percentage_complete))
            self.signals.on_running_script_paused((self.ident, False))
            self.continue_request.callback(True)

    def set_stopping(self):
        self.should_stop = True
        self.status = 'Stopping'
        self.signals.on_running_new_status((self.ident, self.status, self.percentage_complete))
        #if was paused, unpause:
        if self.pause_lock.locked:
            self.pause_lock.release()
    
    def set_pausing(self, should_pause):
        '''if asking to pause, returns a deferred which is fired when sciprt actually paused'''
        self.should_pause = should_pause
        if self.should_pause:
            self.pause_request = Deferred()
            self.status = 'Pausing'
            self.signals.on_running_new_status((self.ident, self.status, self.percentage_complete))
            d = self.pause_lock.acquire()
            return self.pause_request
        else:
            if not self.pause_lock.locked:
                raise Exception ("Trying to unpause script that was not paused")
            self.continue_request = Deferred()
            self.pause_lock.release()
            return self.continue_request
            
    def stop_confirmed(self):
        self.should_stop = False
        self.status = 'Stopped'
        self.signals.on_running_new_status((self.ident, self.status, self.percentage_complete))
        self.signals.on_running_script_stopped(self.ident)
    
    def finish_confirmed(self):
        if self.continue_request is not None:
            if not self.pause_request.called:
                self.pause_request.callback(True)
        if self.continue_request is not None:
            if not self.continue_request.called:
                self.continue_request.callback(True)
        if not self.status == 'Stopped':
            self.percentage_complete = 100.0
            self.status = 'Finished'
            self.signals.on_running_new_status((self.ident, self.status, self.percentage_complete))
        self.signals.on_running_script_finished(self.ident)
    
    def error_finish_confirmed(self, error):
        self.status = 'Error'
        self.signals.on_running_new_status((self.ident, self.status, self.percentage_complete))
        self.signals.on_running_script_finished_error((self.ident, error))